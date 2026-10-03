from __future__ import annotations

import unittest
from uuid import uuid4

from rag_service.domain import AccessPolicy, DocumentSection
from rag_service.ingestion import DeterministicChunker
from rag_service.retrieval import (
    Bm25SparseEncoder,
    HashEmbeddingEncoder,
    PostgresHybridIndex,
    RetrievalConfig,
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

    async def test_group_acl_denies_an_unauthorized_group(self) -> None:
        database_url = test_database_url()
        if database_url is None:
            self.skipTest("RAG_TEST_DATABASE_URL is not set")
        document_id = f"phase2-group-denied-{uuid4().hex}"
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
            [DocumentSection(text="Operations-only launch procedure.")],
            "pg17",
            access_policy=AccessPolicy(groups=("operations",)),
        )
        matches = await HybridRetriever(
            PostgresHybridIndex(database_url, migrations_path="migrations"), embedder, sparse
        ).retrieve(
            "launch procedure",
            top_k=1,
            candidate_k=1,
            filters=RetrievalFilters(
                document_ids=(document_id,), principal="bob", groups=("sales",)
            ),
        )

        self.assertEqual(matches, ())

    async def test_group_acl_allows_an_authorized_group(self) -> None:
        database_url = test_database_url()
        if database_url is None:
            self.skipTest("RAG_TEST_DATABASE_URL is not set")
        document_id = f"phase2-group-allowed-{uuid4().hex}"
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
            [DocumentSection(text="Operations-only launch procedure.")],
            "pg17",
            access_policy=AccessPolicy(groups=("operations",)),
        )
        matches = await HybridRetriever(
            PostgresHybridIndex(database_url, migrations_path="migrations"), embedder, sparse
        ).retrieve(
            "launch procedure",
            top_k=1,
            candidate_k=1,
            filters=RetrievalFilters(
                document_ids=(document_id,), principal="bob", groups=("operations",)
            ),
        )

        self.assertEqual([match.chunk.document_id for match in matches], [document_id])

    async def test_staged_postgres_search_scopes_versions_and_persists_trace(self) -> None:
        database_url = test_database_url()
        if database_url is None:
            self.skipTest("RAG_TEST_DATABASE_URL is not set")
        document_id = f"phase2-staged-{uuid4().hex}"
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
            [DocumentSection(text="PostgreSQL 16 max_wal_senders is 10.")],
            "pg16",
            access_policy=AccessPolicy(public=True),
        )
        store.ingest(
            document_id,
            [DocumentSection(text="PostgreSQL 17 max_wal_senders is 20.")],
            "pg17",
            access_policy=AccessPolicy(public=True),
        )
        retriever = HybridRetriever(
            PostgresHybridIndex(database_url, migrations_path="migrations"),
            embedder,
            sparse,
            config=RetrievalConfig(version_mode="auto", rerank_top_n=2),
        )

        result = await retriever.retrieve_detailed(
            "What is PostgreSQL 17 max_wal_senders?",
            top_k=1,
            candidate_k=2,
            filters=RetrievalFilters(document_ids=(document_id,)),
        )

        self.assertEqual(result.scope.status, "resolved")
        self.assertEqual([match.chunk.version for match in result.matches], ["pg17"])
        self.assertEqual(
            [stage.stage for stage in result.stages],
            ["scope_auth", "dense", "sparse", "fusion", "rerank", "parent_context"],
        )
        with store.database.connect() as connection:
            trace = connection.execute(
                "SELECT stages FROM query_traces WHERE id=%s", (result.trace_id,)
            ).fetchone()
        self.assertIsNotNone(trace)
        assert trace is not None
        self.assertEqual([stage["stage"] for stage in trace["stages"]], [
            "scope_auth", "dense", "sparse", "fusion", "rerank", "parent_context"
        ])


if __name__ == "__main__":
    unittest.main()
