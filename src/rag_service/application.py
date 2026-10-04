"""Use-case orchestration shared by HTTP handlers and background workers."""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterable, Mapping
from dataclasses import dataclass
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
    ) -> None:
        self.pipeline = pipeline
        self.retriever = retriever
        self.generator = generator
        self.max_context_chars = max_context_chars

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
        )
        return PreparedQuery(
            request=request,
            matches=result.matches,
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
        return prepared, await self.generator.generate(prepared.request)

    async def stream_answer(
        self,
        prepared: PreparedQuery,
    ) -> AsyncIterator[str]:
        async for token in self.generator.stream(prepared.request):
            yield token

    def delete_document(self, document_id: str, product_version: str | None = None) -> int:
        delete = getattr(self.pipeline, "delete_document", None)
        if delete is None:
            raise RuntimeError("the configured ingestion backend does not support deletion")
        return int(delete(document_id, product_version))


__all__ = ["PreparedQuery", "RagApplication", "SectionInput"]
