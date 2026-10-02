"""Retrieval ports and local hybrid-search implementation."""

from .encoders import Bm25SparseEncoder, HashEmbeddingEncoder
from .memory import InMemoryHybridIndex
from .models import Citation, RetrievalFilters, ScoredChunk
from .pinecone import PineconeHybridIndex, sparse_term_index
from .service import HybridRetriever

__all__ = [
    "Bm25SparseEncoder",
    "Citation",
    "HashEmbeddingEncoder",
    "HybridRetriever",
    "InMemoryHybridIndex",
    "PineconeHybridIndex",
    "RetrievalFilters",
    "ScoredChunk",
    "sparse_term_index",
]
