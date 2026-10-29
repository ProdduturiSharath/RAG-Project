"""FastAPI entry point for ingestion and grounded query serving."""

from __future__ import annotations

import asyncio
import json
from collections.abc import AsyncIterator, Mapping
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse

from rag_service.application import RagApplication
from rag_service.domain import AccessPolicy, DocumentIdentity, DocumentSection, SourceLocation
from rag_service.generation.models import Claim
from rag_service.retrieval import Citation, RetrievalFilters, ScoredChunk
from rag_service.settings import Settings, load_settings
from rag_service.storage import PostgresJobStore

from .container import build_application
from .schemas import (
    CitationResponse,
    ClaimResponse,
    HealthResponse,
    IngestDocumentRequest,
    IngestDocumentResponse,
    JobResponse,
    MatchResponse,
    QueryRequest,
    QueryResponse,
)
from .security import (
    AuthenticatedPrincipal,
    JWTVerifier,
    RateLimiter,
    enforce_payload_limits,
    security_middleware,
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
    app.state.jwt_verifier = JWTVerifier(settings)
    app.state.rate_limiter = RateLimiter(
        settings.rate_limit_requests, settings.rate_limit_window_seconds
    )
    app.middleware("http")(security_middleware)

    @app.get("/health", response_model=HealthResponse)
    @app.get("/v1/health", response_model=HealthResponse)
    async def health() -> HealthResponse:
        index = application.retriever.index
        return HealthResponse(
            status="ok",
            environment=settings.environment,
            indexed_chunks=int(getattr(index, "public_count", 0)),
        )

    @app.post("/v1/documents", response_model=IngestDocumentResponse)
    async def ingest_document(
        request: Request, payload: IngestDocumentRequest
    ) -> IngestDocumentResponse:
        _require_mutation(request)
        enforce_payload_limits(payload, settings)
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
        request: Request, document_id: str, product_version: str | None = None
    ) -> dict[str, Any]:
        _require_mutation(request)
        try:
            deleted = await asyncio.to_thread(
                application.delete_document, document_id, product_version
            )
        except RuntimeError as exc:
            raise HTTPException(status_code=501, detail=str(exc)) from exc
        return {"document_id": document_id, "product_version": product_version, "deleted": deleted}

    @app.post("/v1/ingestion/jobs", response_model=JobResponse, status_code=202)
    async def enqueue_ingestion(request: Request, payload: IngestDocumentRequest) -> JobResponse:
        _require_mutation(request)
        enforce_payload_limits(payload, settings)
        if settings.storage_backend != "postgres":
            raise HTTPException(
                status_code=501, detail="async ingestion requires the Postgres backend"
            )
        job_store = PostgresJobStore(
            settings.database_url,
            settings.migrations_path,
            connect_timeout_seconds=settings.database_connect_timeout_seconds,
            statement_timeout_ms=settings.database_statement_timeout_ms,
        )
        body = payload.model_dump() if hasattr(payload, "model_dump") else payload.dict()
        job_id = await asyncio.to_thread(job_store.enqueue, "ingest_document", body)
        job = await asyncio.to_thread(job_store.get, job_id)
        if job is None:
            raise HTTPException(status_code=500, detail="job was not persisted")
        return _job_response(job)

    @app.get("/v1/ingestion/jobs/{job_id}", response_model=JobResponse)
    @app.get("/v1/jobs/{job_id}", response_model=JobResponse)
    async def get_ingestion_job(request: Request, job_id: str) -> JobResponse:
        _require_mutation(request)
        if settings.storage_backend != "postgres":
            raise HTTPException(
                status_code=501, detail="async ingestion requires the Postgres backend"
            )
        job = await asyncio.to_thread(
            PostgresJobStore(
                settings.database_url,
                settings.migrations_path,
                connect_timeout_seconds=settings.database_connect_timeout_seconds,
                statement_timeout_ms=settings.database_statement_timeout_ms,
            ).get,
            job_id,
        )
        if job is None:
            raise HTTPException(status_code=404, detail="job not found")
        return _job_response(job)

    @app.post("/v1/query", response_model=QueryResponse)
    async def query(request: Request, payload: QueryRequest) -> QueryResponse:
        principal = _require_auth(request)
        enforce_payload_limits(payload, settings)
        filters = _filters_from_payload(payload, principal)
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
                generation_mode=payload.generation_mode,
                search_mode=payload.search_mode,
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
            answered_version=generated.answered_version,
            claims=[_claim_response(claim) for claim in generated.claims],
            trace_id=prepared.trace_id,
            scope_status=prepared.scope_status,
            scope_versions=list(prepared.scope_versions),
            generation_mode=prepared.generation_mode,
        )

    @app.post("/v1/query/stream")
    async def stream_query(request: Request, payload: QueryRequest) -> StreamingResponse:
        principal = _require_auth(request)
        enforce_payload_limits(payload, settings)
        filters = _filters_from_payload(payload, principal)
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
                generation_mode=payload.generation_mode,
                search_mode=payload.search_mode,
            )
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

        async def events() -> AsyncIterator[str]:
            async with asyncio.timeout(settings.request_timeout_seconds):
                generated = await application.generate_prepared(prepared)
            metadata = {
                "query": payload.query,
                "confidence": generated.confidence,
                "abstained": generated.abstained,
                "answered_version": generated.answered_version,
                "trace_id": prepared.trace_id,
                "generation_mode": prepared.generation_mode,
                "claims": [_claim_response(claim).model_dump() for claim in generated.claims],
                "citations": [_citation_payload(citation) for citation in generated.citations],
            }
            yield _sse("metadata", metadata)
            for token in generated.answer.splitlines(keepends=True):
                yield _sse("token", token)
            yield _sse("done", {})

        return StreamingResponse(
            events(),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        )

    @app.get("/v1/traces/summary")
    async def trace_summary(request: Request) -> dict[str, Any]:
        _require_auth(request)
        summary = getattr(application.retriever.index, "trace_summary", None)
        if summary is None:
            raise HTTPException(status_code=501, detail="trace summaries require a trace store")
        return await asyncio.to_thread(summary)

    @app.get("/v1/corpus/coverage")
    async def corpus_coverage(request: Request) -> dict[str, Any]:
        _require_auth(request)
        coverage = getattr(application.retriever.index, "coverage_summary", None)
        if coverage is None:
            raise HTTPException(status_code=501, detail="corpus coverage requires a storage index")
        return await asyncio.to_thread(coverage)

    @app.get("/v1/traces/{trace_id}")
    async def get_trace(request: Request, trace_id: str) -> dict[str, Any]:
        _require_auth(request)
        getter = getattr(application.retriever.index, "get_trace", None)
        if getter is None:
            raise HTTPException(status_code=501, detail="trace inspection requires a trace store")
        trace = await asyncio.to_thread(getter, trace_id)
        if trace is None:
            raise HTTPException(status_code=404, detail="trace not found")
        return trace

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


def _require_auth(request: Request) -> AuthenticatedPrincipal:
    return request.app.state.jwt_verifier.verify_request(request)


def _require_mutation(request: Request) -> AuthenticatedPrincipal:
    principal = _require_auth(request)
    if not principal.can_mutate():
        raise HTTPException(status_code=403, detail="mutation role required")
    return principal


def _filters_from_payload(
    payload: QueryRequest, principal: AuthenticatedPrincipal
) -> RetrievalFilters:
    return RetrievalFilters(
        document_ids=tuple(payload.document_ids),
        principal=principal.principal,
        groups=principal.groups,
        metadata=payload.metadata,
        product_version=payload.product_version,
        version_mode=payload.version_mode,
        version_selector=payload.version_selector,
    )


def _claim_response(claim: Claim) -> ClaimResponse:
    return ClaimResponse(
        text=claim.text,
        citations=[_citation_response(c) for c in claim.citations],
        supported=claim.supported,
        support_score=claim.support_score,
        reason=claim.reason,
        included=claim.included,
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


class _LazyApp:
    """Defer production model/database initialization until the first request."""

    def __init__(self) -> None:
        self._app: FastAPI | None = None

    def _loaded(self) -> FastAPI:
        if self._app is None:
            self._app = create_app()
        return self._app

    async def __call__(self, scope: Any, receive: Any, send: Any) -> None:
        await self._loaded()(scope, receive, send)

    def __getattr__(self, name: str) -> Any:
        return getattr(self._loaded(), name)


app: Any = _LazyApp()


__all__ = ["app", "create_app", "run"]
