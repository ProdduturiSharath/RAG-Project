"""Provider-independent ingestion primitives."""

from .chunking import (
    Chunker,
    ChunkingConfig,
    DeterministicChunker,
    StructureAwareChunker,
    content_hash_for_sections,
    stable_chunk_id,
    stable_section_id,
)
from .parsers import LocalTextParser, PyMuPDFParser
from .pipeline import IngestionPipeline
from .ports import (
    Embedder,
    EmbedderPort,
    IndexWriter,
    IndexWriterPort,
    Parser,
    ParserPort,
    SparseEncoder,
    SparseEncoderPort,
)

__all__ = [
    "Chunker",
    "ChunkingConfig",
    "DeterministicChunker",
    "Embedder",
    "EmbedderPort",
    "IndexWriter",
    "IndexWriterPort",
    "IngestionPipeline",
    "LocalTextParser",
    "Parser",
    "ParserPort",
    "PyMuPDFParser",
    "SparseEncoder",
    "SparseEncoderPort",
    "StructureAwareChunker",
    "content_hash_for_sections",
    "stable_chunk_id",
    "stable_section_id",
]
