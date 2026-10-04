"""Small local encoders used for development and deterministic tests.

They are intentionally replaceable.  The production wiring can point the same
ports at a hosted embedding model and a learned sparse encoder without changing
the ingestion or query services.
"""

from __future__ import annotations

import hashlib
import math
import re
from collections import Counter
from collections.abc import Iterable, Sequence

_TOKEN_RE = re.compile(r"[a-z0-9]+(?:[-_/.][a-z0-9]+)*(?:\(\d+\))?", re.IGNORECASE)


def tokenize(text: str) -> tuple[str, ...]:
    """Keep complete identifiers and emit searchable component tokens.

    The complete token preserves exact matches while components make names such
    as ``max_wal_senders``, ``pg.stat.activity``, and ``AC-2(1)`` searchable
    when a source and query use different punctuation.
    """

    values: list[str] = []
    for match in _TOKEN_RE.finditer(text):
        token = match.group(0).lower()
        values.append(token)
        values.extend(part for part in re.split(r"[-_/.()]+", token) if part)
    return tuple(values)


def _stable_bucket(value: str, dimensions: int) -> tuple[int, int]:
    digest = hashlib.blake2b(value.encode("utf-8"), digest_size=8).digest()
    number = int.from_bytes(digest, "big")
    bucket = number % dimensions
    sign = 1 if (number >> 63) & 1 else -1
    return bucket, sign


class HashEmbeddingEncoder:
    """A deterministic hashing encoder for local development.

    This is not intended to compete with a semantic embedding model.  It gives
    the project a useful offline vertical slice and makes retrieval regression
    tests independent of network access or provider credentials.
    """

    def __init__(self, dimensions: int = 256) -> None:
        if dimensions < 8:
            raise ValueError("dimensions must be at least 8")
        self.dimensions = dimensions

    def embed(self, texts: Sequence[str]) -> tuple[tuple[float, ...], ...]:
        return tuple(self._embed_one(text) for text in texts)

    def embed_query(self, query: str) -> tuple[float, ...]:
        return self.embed((query,))[0]

    def _embed_one(self, text: str) -> tuple[float, ...]:
        vector = [0.0] * self.dimensions
        terms = tokenize(text)
        features = list(terms)
        features.extend(
            f"{left}\x1f{right}" for left, right in zip(terms, terms[1:], strict=False)
        )
        for feature in features:
            bucket, sign = _stable_bucket(feature, self.dimensions)
            vector[bucket] += float(sign)
        length = math.sqrt(sum(value * value for value in vector))
        if length == 0:
            return tuple(vector)
        return tuple(value / length for value in vector)


class Bm25SparseEncoder:
    """Encode text as a BM25-style sparse vector.

    ``fit`` is optional for the local slice.  Without a corpus, IDF defaults to
    one, preserving exact-token matching.  A worker can fit the encoder against
    the document collection before indexing to obtain corpus-aware IDF weights.
    """

    def __init__(self, *, k1: float = 1.2, b: float = 0.75) -> None:
        if k1 <= 0:
            raise ValueError("k1 must be positive")
        if not 0 <= b <= 1:
            raise ValueError("b must be between zero and one")
        self.k1 = k1
        self.b = b
        self._idf: dict[str, float] = {}
        self._average_length = 1.0

    def fit(self, texts: Iterable[str]) -> Bm25SparseEncoder:
        documents = [tokenize(text) for text in texts]
        if not documents:
            self._idf = {}
            self._average_length = 1.0
            return self
        document_frequency: Counter[str] = Counter()
        for document in documents:
            document_frequency.update(set(document))
        count = len(documents)
        self._idf = {
            token: math.log(1.0 + (count - frequency + 0.5) / (frequency + 0.5))
            for token, frequency in document_frequency.items()
        }
        self._average_length = max(1.0, sum(len(document) for document in documents) / count)
        return self

    def encode(self, texts: Sequence[str]) -> tuple[dict[str, float], ...]:
        return tuple(self._encode_one(text) for text in texts)

    def _encode_one(self, text: str) -> dict[str, float]:
        counts = Counter(tokenize(text))
        length = max(1, sum(counts.values()))
        values: dict[str, float] = {}
        for token, frequency in counts.items():
            idf = self._idf.get(token, 1.0)
            denominator = frequency + self.k1 * (
                1.0 - self.b + self.b * length / self._average_length
            )
            values[token] = idf * (frequency * (self.k1 + 1.0)) / denominator
        return values


__all__ = ["Bm25SparseEncoder", "HashEmbeddingEncoder", "tokenize"]
