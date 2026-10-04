"""Retrieval ports and local hybrid-search implementation."""

from .bm25 import bm25_search
from .encoders import Bm25SparseEncoder, HashEmbeddingEncoder
from .fusion import fuse
from .local_models import CrossEncoderReranker, SentenceTransformerEncoder
from .memory import InMemoryHybridIndex
from .models import (
    Citation,
    RetrievalFilters,
    RetrievalResult,
    ScopeResult,
    ScoredChunk,
    StageTrace,
)
from .pinecone import PineconeHybridIndex, sparse_term_index
from .postgres import PostgresHybridIndex
from .scope import resolve_scope
from .service import HybridRetriever, RetrievalConfig

__all__ = [
    "Bm25SparseEncoder",
    "Citation",
    "CrossEncoderReranker",
    "RetrievalConfig",
    "RetrievalResult",
    "HashEmbeddingEncoder",
    "HybridRetriever",
    "InMemoryHybridIndex",
    "PineconeHybridIndex",
    "PostgresHybridIndex",
    "RetrievalFilters",
    "ScoredChunk",
    "SentenceTransformerEncoder",
    "ScopeResult",
    "StageTrace",
    "bm25_search",
    "fuse",
    "resolve_scope",
    "sparse_term_index",
]
