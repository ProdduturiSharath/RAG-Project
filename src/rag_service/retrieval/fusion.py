"""Inspectably normalized weighted fusion and reciprocal rank fusion."""

from collections.abc import Sequence
from dataclasses import replace

from .models import ScoredChunk


def fuse(dense: Sequence[ScoredChunk], sparse: Sequence[ScoredChunk], *,
         method: str = "rrf", alpha: float = 0.55, rrf_k: int = 60) -> tuple[ScoredChunk, ...]:
    if method not in {"rrf", "weighted"} or not 0 <= alpha <= 1 or rrf_k < 1:
        raise ValueError("invalid fusion configuration")
    records: dict[str, ScoredChunk] = {}
    totals: dict[str, float] = {}
    for values, component, weight in ((dense, "dense_score", alpha),
                                      (sparse, "sparse_score", 1 - alpha)):
        # Max normalization preserves zero relevance and works for singletons.
        scale = max((max(0.0, getattr(v, component)) for v in values), default=0.0)
        for rank, item in enumerate(values, 1):
            key = item.chunk.chunk_id
            records[key] = replace(records.get(key, item), **{component: getattr(item, component)})
            contribution = (1 / (rrf_k + rank) if method == "rrf" else
                            weight * max(0.0, getattr(item, component)) / scale if scale else 0.0)
            totals[key] = totals.get(key, 0.0) + contribution
    ranked = sorted((replace(v, hybrid_score=totals[k]) for k, v in records.items()),
                    key=lambda v: (-v.hybrid_score, v.chunk.chunk_id))
    return tuple(replace(v, rank=i) for i, v in enumerate(ranked, 1))
