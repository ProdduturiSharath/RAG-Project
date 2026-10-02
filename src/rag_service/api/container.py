"""Local application wiring.

The objects in this module are adapters, not business rules.  A deployment can
replace the encoders and index with Pinecone-backed implementations while the
use cases and HTTP contract remain unchanged.
"""

from __future__ import annotations

from rag_service.application import RagApplication
from rag_service.generation import ExtractiveAnswerGenerator
from rag_service.ingestion import ChunkingConfig, DeterministicChunker, IngestionPipeline
from rag_service.retrieval import Bm25SparseEncoder, HashEmbeddingEncoder, InMemoryHybridIndex
from rag_service.retrieval.service import HybridRetriever
from rag_service.settings import Settings, load_settings


def build_application(settings: Settings | None = None) -> RagApplication:
    settings = settings or load_settings()
    dense_encoder = HashEmbeddingEncoder()
    sparse_encoder = Bm25SparseEncoder()
    index = InMemoryHybridIndex()
    chunker = DeterministicChunker(
        config=ChunkingConfig(
            max_tokens=settings.chunk_max_tokens,
            overlap_tokens=settings.chunk_overlap_tokens,
        )
    )
    pipeline = IngestionPipeline(
        chunker,
        embedder=dense_encoder,
        sparse_encoder=sparse_encoder,
        index_writer=index,
    )
    retriever = HybridRetriever(index, dense_encoder, sparse_encoder)
    generator = ExtractiveAnswerGenerator()
    return RagApplication(
        pipeline,
        retriever,
        generator,
        max_context_chars=settings.max_context_chars,
    )


__all__ = ["build_application"]
