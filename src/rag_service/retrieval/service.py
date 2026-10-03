"""Typed orchestration for scope, retrieval, fusion, reranking, and context."""

from __future__ import annotations

import asyncio
import time
import uuid
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

from .fusion import fuse
from .models import RetrievalFilters, RetrievalResult, ScopeResult, ScoredChunk, StageTrace
from .ports import DenseEncoder, Reranker, SparseEncoder, VectorIndex
from .reranking import TokenOverlapReranker
from .scope import resolve_scope


@dataclass(frozen=True, slots=True)
class RetrievalConfig:
    fusion: str = "rrf"
    rerank_top_n: int = 30
    version_mode: str = "none"
    parent_expansion: bool = True


class HybridRetriever:
    """Run typed retrieval stages while retaining the original tuple API."""

    def __init__(
        self,
        index: VectorIndex,
        dense_encoder: DenseEncoder,
        sparse_encoder: SparseEncoder,
        *,
        reranker: Reranker | None = None,
        config: RetrievalConfig | None = None,
    ) -> None:
        self.index = index
        self.dense_encoder = dense_encoder
        self.sparse_encoder = sparse_encoder
        self.reranker = reranker or TokenOverlapReranker()
        self.config = config or RetrievalConfig()
        self.last_result: RetrievalResult | None = None

    async def retrieve(
        self,
        query: str,
        *,
        top_k: int = 5,
        candidate_k: int = 30,
        alpha: float = 0.55,
        filters: RetrievalFilters | None = None,
    ) -> tuple[ScoredChunk, ...]:
        result = await self.retrieve_detailed(
            query, top_k=top_k, candidate_k=candidate_k, alpha=alpha, filters=filters
        )
        self.last_result = result
        return result.matches

    async def retrieve_detailed(
        self,
        query: str,
        *,
        top_k: int = 5,
        candidate_k: int = 30,
        alpha: float = 0.55,
        filters: RetrievalFilters | None = None,
    ) -> RetrievalResult:
        self._validate(query, top_k, candidate_k, alpha)
        filters = filters or RetrievalFilters()
        trace_id = str(uuid.uuid4())
        traces: list[StageTrace] = []

        started = time.perf_counter()
        available = await asyncio.to_thread(
            getattr(self.index, "available_versions", lambda _filters: {}), filters
        )
        scope = resolve_scope(query, filters, available, self.config.version_mode)
        traces.append(self._trace("scope_auth", (), started, {
            "status": scope.status,
            "versions": scope.versions,
        }))
        if scope.status == "ambiguous":
            result = RetrievalResult((), scope, trace_id, tuple(traces))
            self._save_trace(query, scope, result)
            return result

        started = time.perf_counter()
        dense_vector = await self._query_vector(query)
        dense = await asyncio.to_thread(
            self._dense_search, dense_vector, candidate_k, scope.filters
        )
        traces.append(self._trace("dense", dense, started, {"candidate_k": candidate_k}))

        started = time.perf_counter()
        sparse = await asyncio.to_thread(
            self._sparse_search, query, candidate_k, scope.filters
        )
        traces.append(self._trace("sparse", sparse, started, {"candidate_k": candidate_k}))

        started = time.perf_counter()
        fused = fuse(dense, sparse, method=self.config.fusion, alpha=alpha)[:candidate_k]
        traces.append(self._trace("fusion", fused, started, {
            "method": self.config.fusion,
            "alpha": alpha,
        }))

        started = time.perf_counter()
        rerank_count = min(candidate_k, self.config.rerank_top_n)
        reranked = await asyncio.to_thread(
            self.reranker.rerank, query, fused[:rerank_count]
        )
        reranked = tuple(reranked) + tuple(fused[rerank_count:])
        traces.append(self._trace("rerank", reranked, started, {
            "top_n": rerank_count,
            "baseline": type(self.reranker).__name__,
        }))

        started = time.perf_counter()
        expanded = await asyncio.to_thread(
            self._expand_parents, reranked, scope.filters
        ) if self.config.parent_expansion else reranked
        final = tuple(expanded[:top_k])
        traces.append(self._trace("parent_context", final, started, {
            "enabled": self.config.parent_expansion,
        }))
        result = RetrievalResult(final, scope, trace_id, tuple(traces))
        self._save_trace(query, scope, result)
        return result

    async def _query_vector(self, query: str) -> Sequence[float]:
        embed_query = getattr(self.dense_encoder, "embed_query", None)
        if embed_query is not None:
            return await asyncio.to_thread(embed_query, query)
        values = await asyncio.to_thread(self.dense_encoder.embed, (query,))
        if len(values) != 1:
            raise ValueError("query encoder must return exactly one vector")
        return values[0]

    def _dense_search(self, vector: Sequence[float], top_k: int,
                      filters: RetrievalFilters) -> tuple[ScoredChunk, ...]:
        search = getattr(self.index, "dense_search", None)
        if search is not None:
            return tuple(search(vector, top_k=top_k, filters=filters))
        return tuple(self.index.search(vector, {}, top_k=top_k, alpha=1.0, filters=filters))

    def _sparse_search(self, query: str, top_k: int,
                       filters: RetrievalFilters) -> tuple[ScoredChunk, ...]:
        search = getattr(self.index, "sparse_search", None)
        if search is not None:
            return tuple(search(query, top_k=top_k, filters=filters))
        values = self.sparse_encoder.encode((query,))
        if len(values) != 1:
            raise ValueError("query sparse encoder must return exactly one vector")
        return tuple(self.index.search((), values[0], top_k=top_k, alpha=0.0, filters=filters))

    def _expand_parents(self, matches: Sequence[ScoredChunk],
                        filters: RetrievalFilters) -> tuple[ScoredChunk, ...]:
        expand = getattr(self.index, "expand_parents", None)
        if expand is None:
            return tuple(matches)
        return tuple(expand(matches, filters=filters))

    def _save_trace(self, query: str, scope: ScopeResult, result: RetrievalResult) -> None:
        save = getattr(self.index, "save_trace", None)
        if save is not None:
            save(result.trace_id, query, scope.filters, [
                {
                    "stage": trace.stage,
                    "candidates": list(trace.candidates),
                    "elapsed_ms": trace.elapsed_ms,
                    "details": dict(trace.details),
                }
                for trace in result.stages
            ])

    @staticmethod
    def _trace(stage: str, candidates: Sequence[ScoredChunk], started: float,
               details: dict[str, Any]) -> StageTrace:
        return StageTrace(
            stage=stage,
            candidates=tuple({
                "chunk_id": candidate.chunk.chunk_id,
                "document_id": candidate.chunk.document_id,
                "product_version": candidate.chunk.version,
                "dense_score": candidate.dense_score,
                "sparse_score": candidate.sparse_score,
                "hybrid_score": candidate.hybrid_score,
                "rerank_score": candidate.rerank_score,
            } for candidate in candidates),
            elapsed_ms=(time.perf_counter() - started) * 1000,
            details=details,
        )

    @staticmethod
    def _validate(query: str, top_k: int, candidate_k: int, alpha: float) -> None:
        if not query.strip():
            raise ValueError("query cannot be empty")
        if top_k < 1 or candidate_k < top_k:
            raise ValueError("candidate_k must be at least top_k, and both must be positive")
        if not 0 <= alpha <= 1:
            raise ValueError("alpha must be between zero and one")

    def retrieve_sync(
        self,
        query: str,
        *,
        top_k: int = 5,
        candidate_k: int = 30,
        alpha: float = 0.55,
        filters: RetrievalFilters | None = None,
    ) -> tuple[ScoredChunk, ...]:
        """Convenience method for synchronous workers."""

        return asyncio.run(self.retrieve(
            query,
            top_k=top_k,
            candidate_k=candidate_k,
            alpha=alpha,
            filters=filters,
        ))

    @staticmethod
    def confidence(matches: Sequence[ScoredChunk]) -> float:
        """Return a bounded heuristic, not a probabilistic guarantee."""

        if not matches:
            return 0.0
        return max(0.0, min(1.0, matches[0].final_score))


__all__ = ["HybridRetriever", "RetrievalConfig"]
