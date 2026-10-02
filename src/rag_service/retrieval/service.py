"""Async orchestration for first-stage hybrid retrieval and reranking."""

from __future__ import annotations

import asyncio
from collections.abc import Sequence

from .models import RetrievalFilters, ScoredChunk
from .ports import DenseEncoder, Reranker, SparseEncoder, VectorIndex
from .reranking import TokenOverlapReranker


class HybridRetriever:
    """Run dense and sparse query encoding concurrently, then rerank results."""

    def __init__(
        self,
        index: VectorIndex,
        dense_encoder: DenseEncoder,
        sparse_encoder: SparseEncoder,
        *,
        reranker: Reranker | None = None,
    ) -> None:
        self.index = index
        self.dense_encoder = dense_encoder
        self.sparse_encoder = sparse_encoder
        self.reranker = reranker or TokenOverlapReranker()

    async def retrieve(
        self,
        query: str,
        *,
        top_k: int = 5,
        candidate_k: int = 30,
        alpha: float = 0.55,
        filters: RetrievalFilters | None = None,
    ) -> tuple[ScoredChunk, ...]:
        """Return final evidence candidates without blocking the event loop."""

        if not query.strip():
            raise ValueError("query cannot be empty")
        if top_k < 1 or candidate_k < top_k:
            raise ValueError("candidate_k must be at least top_k, and both must be positive")
        if not 0 <= alpha <= 1:
            raise ValueError("alpha must be between zero and one")

        dense_task = asyncio.to_thread(self.dense_encoder.embed, (query,))
        sparse_task = asyncio.to_thread(self.sparse_encoder.encode, (query,))
        dense_values, sparse_values = await asyncio.gather(dense_task, sparse_task)
        if len(dense_values) != 1 or len(sparse_values) != 1:
            raise ValueError("query encoders must each return exactly one vector")

        candidates = await asyncio.to_thread(
            self.index.search,
            dense_values[0],
            sparse_values[0],
            top_k=candidate_k,
            alpha=alpha,
            filters=filters,
        )
        reranked = await asyncio.to_thread(self.reranker.rerank, query, candidates)
        return tuple(reranked[:top_k])

    def retrieve_sync(
        self,
        query: str,
        *,
        top_k: int = 5,
        candidate_k: int = 30,
        alpha: float = 0.55,
        filters: RetrievalFilters | None = None,
    ) -> tuple[ScoredChunk, ...]:
        """Convenience method for workers that are already synchronous."""

        if not query.strip():
            raise ValueError("query cannot be empty")
        dense_values = self.dense_encoder.embed((query,))
        sparse_values = self.sparse_encoder.encode((query,))
        candidates = self.index.search(
            dense_values[0],
            sparse_values[0],
            top_k=candidate_k,
            alpha=alpha,
            filters=filters,
        )
        return tuple(self.reranker.rerank(query, candidates)[:top_k])

    @staticmethod
    def confidence(matches: Sequence[ScoredChunk]) -> float:
        """Return a bounded heuristic, not a probabilistic guarantee."""

        if not matches:
            return 0.0
        return max(0.0, min(1.0, matches[0].final_score))


__all__ = ["HybridRetriever"]
