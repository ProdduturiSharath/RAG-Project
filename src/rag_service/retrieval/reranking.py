"""A transparent local reranker used before a learned cross-encoder."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import replace

from .encoders import tokenize
from .models import ScoredChunk


class TokenOverlapReranker:
    """Favor candidates that contain the query's exact terms.

    Keeping this scorer explainable is useful while the evaluation set is being
    built.  The port can later be replaced by a cross-encoder without changing
    the retrieval service.
    """

    def rerank(self, query: str, candidates: Sequence[ScoredChunk]) -> tuple[ScoredChunk, ...]:
        query_terms = set(tokenize(query))
        rescored: list[ScoredChunk] = []
        for candidate in candidates:
            document_terms = set(tokenize(candidate.chunk.text))
            document_terms.update(tokenize(" ".join(candidate.chunk.section_path)))
            overlap = len(query_terms.intersection(document_terms)) / max(len(query_terms), 1)
            score = 0.65 * candidate.hybrid_score + 0.35 * overlap
            rescored.append(replace(candidate, rerank_score=score))
        rescored.sort(
            key=lambda item: (
                -(item.rerank_score or 0.0),
                -item.sparse_score,
                item.chunk.ordinal,
                item.chunk.chunk_id,
            )
        )
        return tuple(
            replace(candidate, rank=rank)
            for rank, candidate in enumerate(rescored, start=1)
        )


__all__ = ["TokenOverlapReranker"]
