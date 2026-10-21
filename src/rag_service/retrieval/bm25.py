"""Reusable Okapi BM25 baseline.

The old function rebuilt token counts, document frequencies, and average
document length for every query.  Phase 5 evaluates thousands of generated
queries over the same corpus, so the corpus statistics belong in an index.
``bm25_search`` remains as the compatibility wrapper used by the existing
retrieval adapters.
"""

import math
from collections import Counter
from collections.abc import Sequence

from rag_service.domain import Chunk

from .encoders import tokenize
from .models import ScoredChunk


class Bm25Index:
    """An immutable BM25 index for one ordered corpus.

    The scoring formula intentionally matches the original ``bm25_search``
    baseline.  Keeping the chunks and corpus statistics together makes repeated
    searches cheap while preserving the same positive-score filtering and
    deterministic tie-breaking behavior.
    """

    k1 = 1.2
    b = 0.75

    def __init__(self, chunks: Sequence[Chunk]) -> None:
        self.chunks = tuple(chunks)
        self._tokens = tuple(Counter(tokenize(chunk.text)) for chunk in self.chunks)
        self._document_count = len(self._tokens)
        if not self._document_count:
            self._average_length = 1.0
            self._idf: dict[str, float] = {}
            return

        self._average_length = (
            sum(sum(counts.values()) for counts in self._tokens) / self._document_count or 1.0
        )
        document_frequency: Counter[str] = Counter()
        for counts in self._tokens:
            document_frequency.update(counts.keys())
        self._idf = {
            term: math.log(1 + (self._document_count - frequency + 0.5) / (frequency + 0.5))
            for term, frequency in document_frequency.items()
        }

    def search(self, query: str, top_k: int) -> tuple[ScoredChunk, ...]:
        """Return the highest-scoring positive matches for ``query``."""

        if top_k <= 0 or not self._document_count:
            return ()
        terms = set(tokenize(query))
        results: list[ScoredChunk] = []
        for chunk, counts in zip(self.chunks, self._tokens, strict=True):
            length = sum(counts.values())
            score = sum(
                self._idf[term]
                * counts[term]
                * (self.k1 + 1.0)
                / (counts[term] + self.k1 * (1.0 - self.b + self.b * length / self._average_length))
                for term in terms
                if counts[term]
            )
            if score > 0:
                results.append(ScoredChunk(chunk, sparse_score=score))
        return tuple(
            sorted(results, key=lambda value: (-value.sparse_score, value.chunk.chunk_id))[:top_k]
        )

    def __len__(self) -> int:
        return self._document_count


def bm25_search(query: str, chunks: Sequence[Chunk], top_k: int) -> tuple[ScoredChunk, ...]:
    """Compatibility wrapper that builds a one-shot :class:`Bm25Index`."""

    return Bm25Index(chunks).search(query, top_k)


__all__ = ["Bm25Index", "bm25_search"]
