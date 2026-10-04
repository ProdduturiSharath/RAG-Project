"""Okapi BM25 baseline; corpus IDF is applied once, only to document weights."""

import math
from collections import Counter
from collections.abc import Sequence

from rag_service.domain import Chunk

from .encoders import tokenize
from .models import ScoredChunk


def bm25_search(query: str, chunks: Sequence[Chunk], top_k: int) -> tuple[ScoredChunk, ...]:
    tokens = [Counter(tokenize(c.text)) for c in chunks]
    n = len(tokens)
    if not n:
        return ()
    average = sum(sum(t.values()) for t in tokens) / n or 1.0
    df: Counter[str] = Counter()
    for counts in tokens:
        df.update(counts.keys())
    terms = set(tokenize(query))
    results = []
    for chunk, counts in zip(chunks, tokens, strict=True):
        length = sum(counts.values())
        score = sum(math.log(1 + (n - df[t] + 0.5) / (df[t] + 0.5))
                    * counts[t] * 2.2 / (counts[t] + 1.2 * (0.25 + 0.75 * length / average))
                    for t in terms if counts[t])
        if score > 0:
            results.append(ScoredChunk(chunk, sparse_score=score))
    return tuple(sorted(results, key=lambda v: (-v.sparse_score, v.chunk.chunk_id))[:top_k])
