"""Reusable Okapi BM25 baseline.

The old function rebuilt token counts, document frequencies, and average
document length for every query.  Phase 5 evaluates thousands of generated
queries over the same corpus, so the corpus statistics belong in an index.
``bm25_search`` remains as the compatibility wrapper used by the existing
retrieval adapters.
"""

import heapq
import math
from collections import Counter, OrderedDict
from collections.abc import Sequence

from rag_service.domain import Chunk

from .encoders import tokenize
from .models import ScoredChunk

_TOKEN_CACHE_LIMIT = 100_000
_TOKEN_CACHE: OrderedDict[tuple[str, str], Counter[str]] = OrderedDict()


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
        token_counts: list[Counter[str]] = []
        for chunk in self.chunks:
            cache_key = (chunk.chunk_id, chunk.text)
            counts = _TOKEN_CACHE.get(cache_key)
            if counts is None:
                counts = Counter(tokenize(chunk.text))
                _TOKEN_CACHE[cache_key] = counts
                _TOKEN_CACHE.move_to_end(cache_key)
                while len(_TOKEN_CACHE) > _TOKEN_CACHE_LIMIT:
                    _TOKEN_CACHE.popitem(last=False)
            else:
                _TOKEN_CACHE.move_to_end(cache_key)
            token_counts.append(counts)
        self._tokens = tuple(token_counts)
        self._lengths = tuple(sum(counts.values()) for counts in self._tokens)
        self._document_count = len(self._tokens)
        if not self._document_count:
            self._average_length = 1.0
            self._idf: dict[str, float] = {}
            return

        self._average_length = (
            sum(self._lengths) / self._document_count or 1.0
        )
        document_frequency: Counter[str] = Counter()
        postings: dict[str, list[int]] = {}
        for counts in self._tokens:
            document_frequency.update(counts.keys())
        for index, counts in enumerate(self._tokens):
            for term in counts:
                postings.setdefault(term, []).append(index)
        self._idf = {
            term: math.log(1 + (self._document_count - frequency + 0.5) / (frequency + 0.5))
            for term, frequency in document_frequency.items()
        }
        self._postings = {term: tuple(indices) for term, indices in postings.items()}

    def search(self, query: str, top_k: int) -> tuple[ScoredChunk, ...]:
        """Return the highest-scoring positive matches for ``query``."""

        if top_k <= 0 or not self._document_count:
            return ()
        terms = set(tokenize(query))
        candidate_indices = {
            index for term in terms for index in self._postings.get(term, ())
        }
        results: list[ScoredChunk] = []
        for index in candidate_indices:
            chunk = self.chunks[index]
            counts = self._tokens[index]
            length = self._lengths[index]
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
            heapq.nsmallest(
                top_k, results, key=lambda value: (-value.sparse_score, value.chunk.chunk_id)
            )
        )

    def __len__(self) -> int:
        return self._document_count


_INDEX_CACHE_LIMIT = 128
_INDEX_CACHE: OrderedDict[tuple[str, ...], Bm25Index] = OrderedDict()


def cached_bm25_index(chunks: Sequence[Chunk]) -> Bm25Index:
    """Return a cached index keyed by the exact ordered chunk-id subset."""

    ordered_ids = tuple(chunk.chunk_id for chunk in chunks)
    cached = _INDEX_CACHE.get(ordered_ids)
    # Revisions/ACL updates can reuse chunk ids. Never return stale Chunk
    # payloads simply because the ordered id key happens to be unchanged.
    if cached is not None and cached.chunks == tuple(chunks):
        _INDEX_CACHE.move_to_end(ordered_ids)
        return cached
    index = Bm25Index(chunks)
    _INDEX_CACHE[ordered_ids] = index
    _INDEX_CACHE.move_to_end(ordered_ids)
    while len(_INDEX_CACHE) > _INDEX_CACHE_LIMIT:
        _INDEX_CACHE.popitem(last=False)
    return index


def clear_bm25_index_cache() -> None:
    """Clear process-local cached indexes, primarily for bounded tests."""

    _INDEX_CACHE.clear()
    _TOKEN_CACHE.clear()


def bm25_search(query: str, chunks: Sequence[Chunk], top_k: int) -> tuple[ScoredChunk, ...]:
    """Reuse an index for the exact ordered corpus, invalidating changed chunks."""

    return cached_bm25_index(chunks).search(query, top_k)


__all__ = ["Bm25Index", "bm25_search", "cached_bm25_index", "clear_bm25_index_cache"]
