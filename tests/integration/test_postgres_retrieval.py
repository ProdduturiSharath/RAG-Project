from __future__ import annotations

import unittest
from uuid import uuid4

from rag_service.domain import AccessPolicy, DocumentSection
from rag_service.ingestion import DeterministicChunker
from rag_service.retrieval import (
    Bm25SparseEncoder,
    HashEmbeddingEncoder,
    PostgresHybridIndex,
    RetrievalFilters,
)
from rag_service.retrieval.service import HybridRetriever
from rag_service.storage import PostgresVersionedStore
from tests.integration.database import test_database_url


class PostgresRetrievalTests(unittest.IsolatedAsyncioTestCase):
    async def test_acl_and_product_version_are_filtered_before_ranking(self) -> None:
        database_url = test_database_url()
        if database_url is None:
            self.skipTest("RAG_TEST_DATABASE_URL is not set")
        document_id = f"phase1-retrieval-{uuid4().hex}"
        embedder = HashEmbeddingEncoder(dimensions=16)
        sparse = Bm25SparseEncoder()
        store = PostgresVersionedStore(
            database_url,
            DeterministicChunker(max_tokens=50, overlap_tokens=0),
            embedder=embedder,
            sparse_encoder=sparse,
            migrations_path="migrations",
        )
        store.migrate()
        store.ingest(
            document_id,
            [DocumentSection(text="Private pg17 launch date is November 15.")],
            "pg17",
            access_policy=AccessPolicy(principals=("alice",)),
        )
        store.ingest(
            document_id,
            [DocumentSection(text="Public pg16 launch date is October 10.")],
            "pg16",
            access_policy=AccessPolicy(public=True),
        )
        index = PostgresHybridIndex(database_url, migrations_path="migrations")
        retriever = HybridRetriever(index, embedder, sparse)

        denied = await retriever.retrieve(
            "launch date",
            top_k=5,
            candidate_k=5,
            filters=RetrievalFilters(document_ids=(document_id,), principal="bob"),
        )
        scoped = await retriever.retrieve(
            "launch date",
            top_k=5,
            candidate_k=5,
            filters=RetrievalFilters(
                document_ids=(document_id,), principal="alice", product_version="pg17"
            ),
        )

        self.assertEqual({match.chunk.version for match in denied}, {"pg16"})
        self.assertEqual({match.chunk.version for match in scoped}, {"pg17"})
        self.assertEqual({match.chunk.document_id for match in scoped}, {document_id})


if __name__ == "__main__":
    unittest.main()
