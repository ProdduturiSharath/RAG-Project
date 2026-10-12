"""Compose Postgres dense retrieval with the existing, authorized in-process BM25."""

from .memory import InMemoryHybridIndex
from .models import RetrievalFilters, ScoredChunk
from .postgres import PostgresHybridIndex


class PostgresBm25Index(PostgresHybridIndex):
    def __init__(self, database_url: str, *, embedder_id: str,
                 sparse_index: InMemoryHybridIndex) -> None:
        super().__init__(database_url, embedder_id=embedder_id)
        self.sparse_index = sparse_index

    def sparse_search(self, query_text: str, *, top_k: int,
                      filters: RetrievalFilters) -> tuple[ScoredChunk, ...]:
        return self.sparse_index.sparse_search(query_text, top_k=top_k, filters=filters)
