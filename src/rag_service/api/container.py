"""Local application wiring.

The objects in this module are adapters, not business rules.  A deployment can
replace the encoders and index with Pinecone-backed implementations while the
use cases and HTTP contract remain unchanged.
"""

from __future__ import annotations

from typing import Any

from rag_service.application import RagApplication
from rag_service.generation import ExtractiveAnswerGenerator
from rag_service.ingestion import ChunkingConfig, DeterministicChunker, IngestionPipeline
from rag_service.retrieval import (
    Bm25SparseEncoder,
    HashEmbeddingEncoder,
    InMemoryHybridIndex,
    PostgresHybridIndex,
)
from rag_service.retrieval.service import HybridRetriever
from rag_service.settings import Settings, load_settings
from rag_service.storage import PostgresVersionedStore


def build_application(settings: Settings | None = None) -> RagApplication:
    settings = settings or load_settings()
    dense_encoder = HashEmbeddingEncoder()
    sparse_encoder = Bm25SparseEncoder()
    chunker = DeterministicChunker(
        config=ChunkingConfig(
            max_tokens=settings.chunk_max_tokens,
            overlap_tokens=settings.chunk_overlap_tokens,
        )
    )
    index: Any
    pipeline: Any
    if settings.storage_backend == "postgres":
        pipeline = PostgresVersionedStore(
            settings.database_url,
            chunker,
            embedder=dense_encoder,
            sparse_encoder=sparse_encoder,
            embedder_id=settings.embedder_id,
            batch_size=settings.embedding_batch_size,
            migrations_path=settings.migrations_path,
        )
        pipeline.migrate()
        index = PostgresHybridIndex(
            settings.database_url,
            embedder_id=settings.embedder_id,
            migrations_path=settings.migrations_path,
        )
    else:
        index = InMemoryHybridIndex()
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
