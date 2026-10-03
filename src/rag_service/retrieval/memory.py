"""An in-memory hybrid index for local development and contract tests."""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from rag_service.domain import Chunk

from .models import RetrievalFilters, ScoredChunk


@dataclass(frozen=True, slots=True)
class _IndexedChunk:
    chunk: Chunk
    dense_vector: tuple[float, ...] | None
    sparse_vector: Mapping[str, float]


class InMemoryHybridIndex:
    """A tiny Pinecone-shaped index with explicit local scoring.

    It deliberately keeps the same dual-vector contract as the production
    adapter.  That makes the API runnable before a Pinecone index exists and
    gives us a fast test double for authorization and ranking behavior.
    """

    def __init__(self) -> None:
        self._records: dict[str, _IndexedChunk] = {}

    @property
    def count(self) -> int:
        return len(self._records)

    def upsert(
        self,
        chunks: Sequence[Chunk],
        *,
        dense_vectors: Sequence[Sequence[float]] = (),
        sparse_vectors: Sequence[Mapping[str, float]] = (),
    ) -> int:
        if dense_vectors and len(dense_vectors) != len(chunks):
            raise ValueError("dense vector count must match chunk count")
        if sparse_vectors and len(sparse_vectors) != len(chunks):
            raise ValueError("sparse vector count must match chunk count")

        for index, chunk in enumerate(chunks):
            dense = tuple(float(value) for value in dense_vectors[index]) if dense_vectors else None
            sparse = (
                {str(key): float(value) for key, value in sparse_vectors[index].items()}
                if sparse_vectors
                else {}
            )
            self._records[chunk.chunk_id] = _IndexedChunk(chunk, dense, sparse)
        return len(chunks)

    def write(
        self,
        chunks: Sequence[Chunk],
        *,
        dense_vectors: Sequence[Sequence[float]] = (),
        sparse_vectors: Sequence[Mapping[str, float]] = (),
    ) -> None:
        """Implement the ingestion ``IndexWriter`` port."""

        self.upsert(
            chunks,
            dense_vectors=dense_vectors,
            sparse_vectors=sparse_vectors,
        )

    def search(
        self,
        dense_vector: Sequence[float],
        sparse_vector: Mapping[str, float],
        *,
        top_k: int,
        alpha: float,
        filters: RetrievalFilters | None = None,
    ) -> tuple[ScoredChunk, ...]:
        if top_k < 1:
            raise ValueError("top_k must be positive")
        if not 0 <= alpha <= 1:
            raise ValueError("alpha must be between zero and one")

        query_dense = tuple(float(value) for value in dense_vector)
        query_sparse = {str(key): float(value) for key, value in sparse_vector.items()}
        eligible = [
            record
            for record in self._records.values()
            if self._matches(record.chunk, filters)
        ]
        if not eligible:
            return ()

        raw_scores = [
            (
                record,
                self._cosine(query_dense, record.dense_vector),
                self._dot_product(query_sparse, record.sparse_vector),
            )
            for record in eligible
        ]
        dense_scale = max((max(0.0, dense) for _, dense, _ in raw_scores), default=0.0)
        sparse_scale = max((sparse for _, _, sparse in raw_scores), default=0.0)

        ranked: list[ScoredChunk] = []
        for record, dense, sparse in raw_scores:
            dense_component = max(0.0, dense) / dense_scale if dense_scale else 0.0
            sparse_component = sparse / sparse_scale if sparse_scale else 0.0
            if query_dense and query_sparse:
                hybrid = alpha * dense_component + (1.0 - alpha) * sparse_component
            elif query_dense:
                hybrid = dense_component
            elif query_sparse:
                hybrid = sparse_component
            else:
                hybrid = 0.0
            ranked.append(
                ScoredChunk(
                    chunk=record.chunk,
                    dense_score=dense,
                    sparse_score=sparse,
                    hybrid_score=hybrid,
                )
            )

        ranked.sort(
            key=lambda item: (
                -item.hybrid_score,
                -item.sparse_score,
                item.chunk.ordinal,
                item.chunk.chunk_id,
            )
        )
        return tuple(
            ScoredChunk(
                chunk=item.chunk,
                dense_score=item.dense_score,
                sparse_score=item.sparse_score,
                hybrid_score=item.hybrid_score,
                rank=rank,
            )
            for rank, item in enumerate(ranked[:top_k], start=1)
        )

    def delete_document(self, document_id: str, version: str | None = None) -> int:
        """Remove a document revision, useful for replacement and retention jobs."""

        to_delete = [
            chunk_id
            for chunk_id, record in self._records.items()
            if record.chunk.document_id == document_id
            and (version is None or record.chunk.version == version)
        ]
        for chunk_id in to_delete:
            del self._records[chunk_id]
        return len(to_delete)

    def clear(self) -> None:
        self._records.clear()

    @staticmethod
    def _cosine(left: Sequence[float], right: Sequence[float] | None) -> float:
        if not left or not right or len(left) != len(right):
            return 0.0
        numerator = sum(a * b for a, b in zip(left, right, strict=False))
        left_norm = math.sqrt(sum(value * value for value in left))
        right_norm = math.sqrt(sum(value * value for value in right))
        if left_norm == 0 or right_norm == 0:
            return 0.0
        return numerator / (left_norm * right_norm)

    @staticmethod
    def _dot_product(left: Mapping[str, float], right: Mapping[str, float]) -> float:
        if len(left) > len(right):
            left, right = right, left
        return sum(value * right.get(key, 0.0) for key, value in left.items())

    @staticmethod
    def _matches(chunk: Chunk, filters: RetrievalFilters | None) -> bool:
        if filters is None:
            filters = RetrievalFilters()
        if filters.document_ids and chunk.document_id not in filters.document_ids:
            return False
        if filters.product_version is not None and chunk.version != filters.product_version:
            return False
        policy = chunk.access_policy
        if policy is not None and not policy.allows(filters.principal, groups=filters.groups):
            return False
        metadata = dict(chunk.metadata)
        metadata.update(chunk.page_metadata)
        return all(metadata.get(key) == value for key, value in filters.metadata.items())


__all__ = ["InMemoryHybridIndex"]
