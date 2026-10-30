"""Use-case orchestration shared by HTTP handlers and background workers."""

from __future__ import annotations

import asyncio
import time
from collections.abc import AsyncIterator, Iterable, Mapping
from dataclasses import dataclass, replace
from typing import Any, Literal

from rag_service.domain import (
    AccessPolicy,
    DocumentIdentity,
    DocumentSection,
    DocumentVersion,
    IngestionResult,
    SourceLocation,
)
from rag_service.generation import AnswerGenerator, GeneratedAnswer, GenerationRequest
from rag_service.generation.extractive import ExtractiveAnswerGenerator
from rag_service.generation.prompting import authorized_request
from rag_service.generation.verification import abstention, annotate, verify_answer
from rag_service.retrieval import HybridRetriever, RetrievalFilters, ScoredChunk

SectionInput = DocumentSection | Mapping[str, object]
GenerationMode = Literal["extractive", "verified", "unverified"]


@dataclass(frozen=True, slots=True)
class PreparedQuery:
    """Evidence and generation input produced before answer streaming."""

    request: GenerationRequest
    matches: tuple[ScoredChunk, ...]
    trace_id: str | None = None
    scope_status: str = "resolved"
    scope_versions: tuple[str, ...] = ()
    generation_mode: GenerationMode = "verified"
    started_at: float = 0.0


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
        extractive_generator: AnswerGenerator | None = None,
    ) -> None:
        self.pipeline = pipeline
        self.retriever = retriever
        self.generator = generator
        self.extractive_generator = extractive_generator or ExtractiveAnswerGenerator()
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
        generation_mode: GenerationMode = "verified",
        search_mode: str | None = None,
    ) -> PreparedQuery:
        self._validate_generation_mode(generation_mode)
        started_at = time.perf_counter()
        result = await self.retriever.retrieve_detailed(
            query,
            top_k=top_k,
            candidate_k=candidate_k,
            alpha=alpha,
            filters=filters,
            search_mode=search_mode,
        )
        request = GenerationRequest(
            query=query,
            matches=result.matches,
            max_context_chars=self.max_context_chars,
            filters=result.scope.filters,
            answered_version=(result.scope.filters.product_version or (
                result.scope.versions[0] if len(result.scope.versions) == 1 else None
            )),
            scope_status=result.scope.status,
        )
        request = authorized_request(request)
        # Private evidence may be used by the local extractive fallback, but it
        # must never leave the machine for an external provider.  The selected
        # generation mode, rather than the configured default generator, decides
        # whether the public-only boundary is required.
        if getattr(self.generator, "external_provider", False) and generation_mode != "extractive":
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
            generation_mode=generation_mode,
            started_at=started_at,
        )

    async def answer(
        self,
        query: str,
        *,
        top_k: int,
        candidate_k: int,
        alpha: float,
        filters: RetrievalFilters | None = None,
        generation_mode: GenerationMode = "verified",
        search_mode: str | None = None,
    ) -> tuple[PreparedQuery, GeneratedAnswer]:
        prepared = await self.prepare_query(
            query,
            top_k=top_k,
            candidate_k=candidate_k,
            alpha=alpha,
            filters=filters,
            generation_mode=generation_mode,
            search_mode=search_mode,
        )
        return prepared, await self.generate_prepared(prepared)

    async def generate_prepared(self, prepared: PreparedQuery) -> GeneratedAnswer:
        request = authorized_request(prepared.request)
        if not request.matches:
            result = abstention(reason="no_authorized_evidence")
        else:
            generator = (
                self.extractive_generator
                if prepared.generation_mode == "extractive"
                else self.generator
            )
            answer = await generator.generate(request)
            if prepared.generation_mode == "verified" and self.verify_generation:
                result = verify_answer(answer, request, threshold=self.abstention_threshold)
            else:
                result = annotate(answer, request)
        if result.answered_version is None and request.answered_version is not None:
            result = replace(result, answered_version=request.answered_version)
        result = self._with_generation_metadata(result, prepared.generation_mode)
        self._record_trace(prepared, result)
        return result

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

    @staticmethod
    def _validate_generation_mode(mode: str) -> None:
        if mode not in {"extractive", "verified", "unverified"}:
            raise ValueError("generation_mode must be extractive, verified, or unverified")

    @staticmethod
    def _with_generation_metadata(answer: GeneratedAnswer, mode: str) -> GeneratedAnswer:
        metadata = dict(answer.metadata)
        metadata.update(
            {
                "generation_mode": mode,
                "generator": (
                    "extractive" if mode == "extractive" else metadata.get("model", "local")
                ),
                "cost_usd": float(metadata.get("cost_usd", 0.0) or 0.0),
                "cost_basis": metadata.get("cost_basis", "local-extractive"),
            }
        )
        return replace(answer, metadata=metadata)

    def _record_trace(self, prepared: PreparedQuery, answer: GeneratedAnswer) -> None:
        if prepared.trace_id is None:
            return
        update = getattr(self.retriever.index, "update_trace", None)
        if update is None:
            return
        cost = float(answer.metadata.get("cost_usd", 0.0) or 0.0)
        update(
            prepared.trace_id,
            metadata={
                "generation_mode": prepared.generation_mode,
                "generator": answer.metadata.get("generator", "local"),
                "abstained": answer.abstained,
                "confidence": answer.confidence,
                "answered_version": answer.answered_version,
                "scope_status": prepared.scope_status,
                "cost_basis": answer.metadata.get("cost_basis", "local-extractive"),
                "model": answer.metadata.get("model"),
                "usage": answer.metadata.get("usage"),
                "cost_estimate": answer.metadata.get("cost_estimate"),
                "provider_latency_seconds": answer.metadata.get("latency_seconds"),
                "attempts": answer.metadata.get("attempts"),
            },
            generation_mode=prepared.generation_mode,
            cost_usd=cost,
            latency_ms=(time.perf_counter() - prepared.started_at) * 1000
            if prepared.started_at
            else None,
        )


__all__ = ["PreparedQuery", "RagApplication", "SectionInput"]
