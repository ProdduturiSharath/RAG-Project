"""Use-case orchestration shared by HTTP handlers and background workers."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator, Iterable, Mapping
from dataclasses import dataclass, replace
from typing import Any

from rag_service.domain import (
    AccessPolicy,
    DocumentIdentity,
    DocumentSection,
    DocumentVersion,
    IngestionResult,
    SourceLocation,
)
from rag_service.generation import AnswerGenerator, GeneratedAnswer, GenerationRequest
from rag_service.generation.prompting import authorized_request
from rag_service.generation.verification import abstention, annotate, verify_answer
from rag_service.retrieval import HybridRetriever, RetrievalFilters, ScoredChunk

SectionInput = DocumentSection | Mapping[str, object]


@dataclass(frozen=True, slots=True)
class PreparedQuery:
    """Evidence and generation input produced before answer streaming."""

    request: GenerationRequest
    matches: tuple[ScoredChunk, ...]
    trace_id: str | None = None
    scope_status: str = "resolved"
    scope_versions: tuple[str, ...] = ()


class RagApplication:
    """Coordinate ingestion, retrieval, and grounded answer generation."""

    def __init__(
        self,
        pipeline: Any,
        retriever: HybridRetriever,
        generator: AnswerGenerator,
        *,
        max_context_chars: int = 18_000,
        verify_generation: bool = False,
        abstention_threshold: float = 0.0,
    ) -> None:
        self.pipeline = pipeline
        self.retriever = retriever
        self.generator = generator
        self.max_context_chars = max_context_chars
        self.verify_generation = verify_generation
        self.abstention_threshold = abstention_threshold

    def ingest(
        self,
        document: DocumentIdentity | str,
        sections: Iterable[SectionInput] | str,
        version: DocumentVersion | str | None = None,
        *,
        content_hash: str | None = None,
        source: SourceLocation | None = None,
        access_policy: AccessPolicy | None = None,
    ) -> IngestionResult:
        return self.pipeline.ingest(
            document,
            sections,
            version,
            content_hash=content_hash,
            source=source,
            access_policy=access_policy,
        )

    async def prepare_query(
        self,
        query: str,
        *,
        top_k: int,
        candidate_k: int,
        alpha: float,
        filters: RetrievalFilters | None = None,
    ) -> PreparedQuery:
        result = await self.retriever.retrieve_detailed(
            query,
            top_k=top_k,
            candidate_k=candidate_k,
            alpha=alpha,
            filters=filters,
        )
        request = GenerationRequest(
            query=query,
            matches=result.matches,
            max_context_chars=self.max_context_chars,
            filters=filters or RetrievalFilters(),
            answered_version=(filters.product_version if filters else None) or (
                result.scope.versions[0] if len(result.scope.versions) == 1 else None
            ),
            scope_status=result.scope.status,
        )
        request = authorized_request(request)
        if getattr(self.generator, "external_provider", False):
            public_chunks = getattr(self.retriever.index, "external_public_chunks", None)
            if public_chunks is not None:
                matches = await asyncio.to_thread(public_chunks, request.matches, request.filters)
                request = replace(request, matches=tuple(matches))
            request = authorized_request(request, public_only=True)
        return PreparedQuery(
            request=request,
            matches=request.matches,
            trace_id=result.trace_id,
            scope_status=result.scope.status,
            scope_versions=result.scope.versions,
        )

    async def answer(
        self,
        query: str,
        *,
        top_k: int,
        candidate_k: int,
        alpha: float,
        filters: RetrievalFilters | None = None,
    ) -> tuple[PreparedQuery, GeneratedAnswer]:
        prepared = await self.prepare_query(
            query,
            top_k=top_k,
            candidate_k=candidate_k,
            alpha=alpha,
            filters=filters,
        )
        return prepared, await self.generate_prepared(prepared)

    async def generate_prepared(self, prepared: PreparedQuery) -> GeneratedAnswer:
        request = authorized_request(prepared.request)
        if not request.matches:
            return abstention(reason="no_authorized_evidence")
        answer = await self.generator.generate(request)
        if self.verify_generation:
            return verify_answer(answer, request, threshold=self.abstention_threshold)
        return annotate(answer, request)

    async def stream_answer(
        self,
        prepared: PreparedQuery,
    ) -> AsyncIterator[str]:
        answer = await self.generate_prepared(prepared)
        yield answer.answer

    def delete_document(self, document_id: str, product_version: str | None = None) -> int:
        delete = getattr(self.pipeline, "delete_document", None)
        if delete is None:
            raise RuntimeError("the configured ingestion backend does not support deletion")
        return int(delete(document_id, product_version))


__all__ = ["PreparedQuery", "RagApplication", "SectionInput"]
