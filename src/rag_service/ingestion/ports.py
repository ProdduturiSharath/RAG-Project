"""Protocols for optional ingestion integrations.

Concrete adapters can implement these small synchronous ports without making
the domain depend on a parser library, embedding vendor, or index backend.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from typing import Protocol, runtime_checkable

from rag_service.domain import Chunk, DocumentSection, SourceLocation


@runtime_checkable
class Parser(Protocol):
    """Convert a source into ordered structural sections."""

    def parse(
        self,
        source: SourceLocation,
    ) -> Iterable[DocumentSection | Mapping[str, object]]:
        """Return sections in source order without performing indexing."""


@runtime_checkable
class Embedder(Protocol):
    """Create dense vectors for chunk text."""

    def embed(self, texts: Sequence[str]) -> Sequence[Sequence[float]]:
        """Return one dense vector for each input text."""


@runtime_checkable
class SparseEncoder(Protocol):
    """Create sparse term-weight mappings for chunk text."""

    def encode(self, texts: Sequence[str]) -> Sequence[Mapping[str, float]]:
        """Return one sparse vector for each input text."""


@runtime_checkable
class IndexWriter(Protocol):
    """Persist chunks and optional vectors in a retrieval index."""

    def write(
        self,
        chunks: Sequence[Chunk],
        *,
        dense_vectors: Sequence[Sequence[float]] = (),
        sparse_vectors: Sequence[Mapping[str, float]] = (),
    ) -> None:
        """Persist one batch atomically from the pipeline's perspective."""


# Explicit ``Port`` aliases are convenient for codebases that reserve the
# shorter names for implementations.
ParserPort = Parser
EmbedderPort = Embedder
SparseEncoderPort = SparseEncoder
IndexWriterPort = IndexWriter

__all__ = [
    "Embedder",
    "EmbedderPort",
    "IndexWriter",
    "IndexWriterPort",
    "Parser",
    "ParserPort",
    "SparseEncoder",
    "SparseEncoderPort",
]
