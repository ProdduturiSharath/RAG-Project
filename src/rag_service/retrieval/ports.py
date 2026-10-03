"""Small ports that keep the application independent from a vector vendor."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol

from .models import RetrievalFilters, ScoredChunk


class DenseEncoder(Protocol):
    def embed(self, texts: Sequence[str]) -> Sequence[Sequence[float]]:
        """Return one dense vector per input text."""


class SparseEncoder(Protocol):
    def encode(self, texts: Sequence[str]) -> Sequence[dict[str, float]]:
        """Return one sparse term-weight map per input text."""


class VectorIndex(Protocol):
    def search(
        self,
        dense_vector: Sequence[float],
        sparse_vector: dict[str, float],
        *,
        top_k: int,
        alpha: float,
        filters: RetrievalFilters | None = None,
    ) -> Sequence[ScoredChunk]:
        """Return the best authorized candidates."""


class Reranker(Protocol):
    def rerank(self, query: str, candidates: Sequence[ScoredChunk]) -> Sequence[ScoredChunk]:
        """Re-score candidates with a second-stage model."""


__all__ = ["DenseEncoder", "Reranker", "SparseEncoder", "VectorIndex"]
