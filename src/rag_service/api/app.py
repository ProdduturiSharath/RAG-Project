"""FastAPI entry point for ingestion and grounded query serving."""

from __future__ import annotations

import asyncio
import json
from collections.abc import AsyncIterator, Mapping
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse

from rag_service.application import RagApplication
from rag_service.domain import AccessPolicy, DocumentIdentity, DocumentSection, SourceLocation
from rag_service.retrieval import Citation, RetrievalFilters, ScoredChunk
from rag_service.settings import Settings, load_settings
from rag_service.storage import PostgresJobStore

from .container import build_application
from .schemas import (
    CitationResponse,
    HealthResponse,
    IngestDocumentRequest,
    IngestDocumentResponse,
    JobResponse,
    MatchResponse,
    QueryRequest,
    QueryResponse,
)


def create_app(
    application: RagApplication | None = None,
    settings: Settings | None = None,
) -> FastAPI:
    """Create an app instance, optionally with test-specific dependencies."""

    settings = settings or load_settings()
    application = application or build_application(settings)
    app = FastAPI(
        title="Evidence RAG API",
        version="0.1.0",
        description="Hybrid retrieval with evidence-first answer generation.",
    )
    app.state.rag = application
    app.state.settings = settings

    @app.get("/health", response_model=HealthResponse)
    async def health() -> HealthResponse:
        index = application.retriever.index
        return HealthResponse(
            status="ok",
            environment=settings.environment,
            indexed_chunks=int(getattr(index, "count", 0)),
        )

    @app.post("/v1/documents", response_model=IngestDocumentResponse)
    async def ingest_document(payload: IngestDocumentRequest) -> IngestDocumentResponse:
        source = _source_from_payload(payload.source)
        access_policy = _policy_from_payload(payload.access_policy)
        sections = tuple(_section_from_payload(section, source) for section in payload.sections)
        if not sections:
            if payload.text is None or not payload.text.strip():
                raise HTTPException(
                    status_code=422,
                    detail="Provide at least one section or a non-empty text field",
                )
            sections = (DocumentSection(text=payload.text, source=source),)

        identity = DocumentIdentity(
            document_id=payload.document_id,
            source=source,
            title=payload.title,
            access_policy=access_policy,
        )
        try:
            result = await asyncio.to_thread(
                application.ingest,
                identity,
                sections,
                payload.version,
                content_hash=payload.content_hash,
                source=source,
                access_policy=access_policy,
            )
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        return IngestDocumentResponse(
            document_id=result.document_id,
            version=result.version,
            content_hash=result.content_hash,
            ingestion_id=result.ingestion_id,
            chunk_count=result.chunk_count,
            already_ingested=result.already_ingested,
            revision=result.revision,
        )

    @app.delete("/v1/documents/{document_id}")
    async def delete_document(
        document_id: str, product_version: str | None = None
    ) -> dict[str, Any]:
        try:
            deleted = await asyncio.to_thread(
                application.delete_document, document_id, product_version
            )
        except RuntimeError as exc:
            raise HTTPException(status_code=501, detail=str(exc)) from exc
        return {"document_id": document_id, "product_version": product_version, "deleted": deleted}

    @app.post("/v1/ingestion/jobs", response_model=JobResponse, status_code=202)
    async def enqueue_ingestion(payload: IngestDocumentRequest) -> JobResponse:
        if settings.storage_backend != "postgres":
            raise HTTPException(
                status_code=501, detail="async ingestion requires the Postgres backend"
            )
        job_store = PostgresJobStore(settings.database_url, settings.migrations_path)
        body = payload.model_dump() if hasattr(payload, "model_dump") else payload.dict()
        job_id = await asyncio.to_thread(job_store.enqueue, "ingest_document", body)
        job = await asyncio.to_thread(job_store.get, job_id)
        if job is None:
            raise HTTPException(status_code=500, detail="job was not persisted")
        return _job_response(job)

    @app.get("/v1/ingestion/jobs/{job_id}", response_model=JobResponse)
    async def get_ingestion_job(job_id: str) -> JobResponse:
        if settings.storage_backend != "postgres":
            raise HTTPException(
                status_code=501, detail="async ingestion requires the Postgres backend"
            )
        job = await asyncio.to_thread(
            PostgresJobStore(settings.database_url, settings.migrations_path).get, job_id
        )
        if job is None:
            raise HTTPException(status_code=404, detail="job not found")
        return _job_response(job)

    @app.post("/v1/query", response_model=QueryResponse)
    async def query(payload: QueryRequest) -> QueryResponse:
        filters = _filters_from_payload(payload)
        top_k = payload.top_k or settings.retrieval_top_k
        candidate_k = payload.candidate_k or max(settings.retrieval_candidate_k, top_k)
        alpha = settings.hybrid_alpha if payload.alpha is None else payload.alpha
        try:
            prepared, generated = await application.answer(
                payload.query,
                top_k=top_k,
                candidate_k=candidate_k,
                alpha=alpha,
                filters=filters,
            )
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        return QueryResponse(
            query=payload.query,
            answer=generated.answer,
            citations=[_citation_response(citation) for citation in generated.citations],
            matches=[_match_response(match) for match in prepared.matches],
            confidence=generated.confidence,
            abstained=generated.abstained,
            trace_id=prepared.trace_id,
            scope_status=prepared.scope_status,
            scope_versions=list(prepared.scope_versions),
        )

    @app.post("/v1/query/stream")
    async def stream_query(payload: QueryRequest) -> StreamingResponse:
        filters = _filters_from_payload(payload)
        top_k = payload.top_k or settings.retrieval_top_k
        candidate_k = payload.candidate_k or max(settings.retrieval_candidate_k, top_k)
        alpha = settings.hybrid_alpha if payload.alpha is None else payload.alpha
        try:
            prepared = await application.prepare_query(
                payload.query,
                top_k=top_k,
                candidate_k=candidate_k,
                alpha=alpha,
                filters=filters,
            )
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

        async def events() -> AsyncIterator[str]:
            confidence = application.retriever.confidence(prepared.matches)
            minimum_score = float(getattr(application.generator, "minimum_score", 0.0))
            metadata = {
                "query": payload.query,
                "confidence": confidence,
                "abstained": not prepared.matches or confidence < minimum_score,
                "citations": [
                    _citation_payload(match.citation()) for match in prepared.matches
                ],
            }
            yield _sse("metadata", metadata)
            async for token in application.stream_answer(prepared):
                yield _sse("token", token)
            yield _sse("done", {})

        return StreamingResponse(
            events(),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        )

    return app


def _source_from_payload(payload: Any) -> SourceLocation | None:
    if payload is None:
        return None
    if not payload.uri and not payload.path:
        return None
    return SourceLocation(
        uri=payload.uri,
        path=payload.path,
        page_number=payload.page_number,
        fragment=payload.fragment,
        metadata=payload.metadata,
    )


def _policy_from_payload(payload: Any) -> AccessPolicy | None:
    if payload is None:
        return None
    return AccessPolicy(
        public=payload.public,
        principals=tuple(payload.principals),
        groups=tuple(payload.groups),
        metadata=payload.metadata,
    )


def _section_from_payload(payload: Any, source: SourceLocation | None) -> DocumentSection:
    return DocumentSection(
        text=payload.text,
        heading=payload.heading,
        level=payload.level,
        section_path=tuple(payload.section_path),
        page_number=payload.page_number,
        page_metadata=payload.page_metadata,
        metadata=payload.metadata,
        section_id=payload.section_id,
        parent_section_id=payload.parent_section_id,
        source=source,
    )


def _filters_from_payload(payload: QueryRequest) -> RetrievalFilters:
    return RetrievalFilters(
        document_ids=tuple(payload.document_ids),
        principal=payload.principal,
        groups=tuple(payload.groups),
        metadata=payload.metadata,
        product_version=payload.product_version,
        version_mode=payload.version_mode,
        version_selector=payload.version_selector,
    )


def _citation_response(citation: Citation) -> CitationResponse:
    return CitationResponse(
        chunk_id=citation.chunk_id,
        document_id=citation.document_id,
        version=citation.version,
        product_version=citation.product_version,
        source_uri=citation.source_uri,
        page_number=citation.page_number,
        section_path=list(citation.section_path),
        excerpt=citation.excerpt,
        revision=citation.revision,
    )


def _citation_payload(citation: Citation) -> dict[str, Any]:
    response = _citation_response(citation)
    if hasattr(response, "model_dump"):
        return response.model_dump()
    return response.dict()


def _match_response(match: ScoredChunk) -> MatchResponse:
    chunk = match.chunk
    return MatchResponse(
        chunk_id=chunk.chunk_id,
        document_id=chunk.document_id,
        version=chunk.version,
        product_version=chunk.product_version,
        text=chunk.text,
        section_path=list(chunk.section_path),
        page_number=chunk.page_number,
        dense_score=match.dense_score,
        sparse_score=match.sparse_score,
        hybrid_score=match.hybrid_score,
        rerank_score=match.rerank_score,
        rank=match.rank,
    )


def _sse(event: str, data: Any) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


def _job_response(job: Mapping[str, Any]) -> JobResponse:
    return JobResponse(
        id=str(job["id"]),
        kind=str(job["kind"]),
        status=str(job["status"]),
        attempts=int(job["attempts"]),
        error=job.get("error"),
        result=job.get("result"),
        created_at=_isoformat(job.get("created_at")),
        started_at=_isoformat(job.get("started_at")),
        finished_at=_isoformat(job.get("finished_at")),
    )


def _isoformat(value: Any) -> str | None:
    return value.isoformat() if value is not None and hasattr(value, "isoformat") else value


def run() -> None:
    """Run the development server via the project script."""

    import uvicorn

    uvicorn.run("rag_service.api.app:create_app", factory=True, host="127.0.0.1", port=8000)


app = create_app()


__all__ = ["app", "create_app", "run"]
