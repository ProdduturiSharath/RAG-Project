"""Local application wiring.

The objects in this module are adapters, not business rules.  A deployment can
replace the encoders and index with Pinecone-backed implementations while the
use cases and HTTP contract remain unchanged.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from rag_service.application import RagApplication
from rag_service.generation import (
    AnswerGenerator,
    ExtractiveAnswerGenerator,
    OpenAICompatibleGenerator,
)
from rag_service.generation.openai_compatible import deepseek_key
from rag_service.ingestion import ChunkingConfig, DeterministicChunker, IngestionPipeline
from rag_service.retrieval import (
    Bm25SparseEncoder,
    CrossEncoderReranker,
    HashEmbeddingEncoder,
    InMemoryHybridIndex,
    PostgresHybridIndex,
    RetrievalConfig,
    SentenceTransformerEncoder,
)
from rag_service.retrieval.reranking import TokenOverlapReranker
from rag_service.retrieval.service import HybridRetriever
from rag_service.settings import Settings, load_settings
from rag_service.storage import PostgresVersionedStore


def build_application(settings: Settings | None = None) -> RagApplication:
    settings = settings or load_settings()
    dense_encoder = (
        HashEmbeddingEncoder()
        if settings.dense_model == "hash-v1"
        else SentenceTransformerEncoder(
            settings.dense_model,
            metadata_prefixed=settings.metadata_prefixed_embeddings,
            query_instruction=settings.query_instruction,
        )
    )
    sparse_encoder = Bm25SparseEncoder()
    chunker = DeterministicChunker(
        config=ChunkingConfig(
            max_tokens=settings.chunk_max_tokens,
            overlap_tokens=settings.chunk_overlap_tokens,
        )
    )
    index: Any
    pipeline: Any
    embedder_id = settings.embedder_id
    if settings.dense_model != "hash-v1" and embedder_id == "hash-v1":
        embedder_id = settings.dense_model
    if settings.storage_backend == "postgres":
        pipeline = PostgresVersionedStore(
            settings.database_url,
            chunker,
            embedder=dense_encoder,
            sparse_encoder=sparse_encoder,
            embedder_id=embedder_id,
            batch_size=settings.embedding_batch_size,
            migrations_path=settings.migrations_path,
        )
        pipeline.migrate()
        index = PostgresHybridIndex(
            settings.database_url,
            embedder_id=embedder_id,
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
    reranker = (
        TokenOverlapReranker()
        if settings.reranker_model == "token-overlap"
        else CrossEncoderReranker(settings.reranker_model)
    )
    retriever = HybridRetriever(
        index,
        dense_encoder,
        sparse_encoder,
        reranker=reranker,
        config=RetrievalConfig(
            fusion=settings.fusion_method,
            rerank_top_n=settings.rerank_top_n,
            version_mode=settings.version_mode,
            parent_expansion=settings.parent_expansion,
        ),
    )
    generator: AnswerGenerator = ExtractiveAnswerGenerator()
    threshold = 0.0
    if settings.generation_backend == "deepseek-flash":
        calibration_path = Path(__file__).resolve().parents[3] / "configs/phase6_calibration.json"
        calibration = json.loads(calibration_path.read_text(encoding="utf-8"))
        threshold = float(calibration["calibration"]["llm"]["threshold"])
        generator = OpenAICompatibleGenerator(api_key=deepseek_key(), verified=False)
    return RagApplication(
        pipeline,
        retriever,
        generator,
        max_context_chars=settings.max_context_chars,
        verify_generation=settings.generation_backend == "deepseek-flash",
        abstention_threshold=threshold,
    )


__all__ = ["build_application"]
