from __future__ import annotations

import os
import unittest
from uuid import uuid4

from rag_service.storage import PostgresDatabase, PostgresJobStore


class PostgresSchemaAndJobTests(unittest.TestCase):
    def setUp(self) -> None:
        database_url = os.getenv("RAG_TEST_DATABASE_URL")
        if database_url is None:
            self.skipTest("RAG_TEST_DATABASE_URL is not set")
        self.database_url = database_url
        self.database = PostgresDatabase(database_url, "migrations")
        self.database.migrate()

    def test_required_schema_and_pgvector_features_are_present(self) -> None:
        with self.database.connect() as connection:
            connection.execute("LOAD 'vector'")
            extension = connection.execute(
                "SELECT extversion FROM pg_extension WHERE extname = 'vector'"
            ).fetchone()
            tables = connection.execute(
                """
                SELECT table_name FROM information_schema.tables
                WHERE table_schema = 'public' AND table_name = ANY(%s)
                """,
                (
                    [
                        "documents",
                        "document_versions",
                        "sections",
                        "chunks",
                        "embeddings",
                        "acl",
                        "jobs",
                        "query_traces",
                    ],
                ),
            ).fetchall()
            indexes = connection.execute(
                "SELECT indexname FROM pg_indexes WHERE indexname = 'document_versions_one_active'"
            ).fetchall()
            settings = connection.execute(
                """
                SELECT name FROM pg_settings
                WHERE name IN ('hnsw.iterative_scan', 'ivfflat.iterative_scan')
                """
            ).fetchall()

        assert extension is not None
        self.assertEqual(extension["extversion"], "0.8.7")
        self.assertEqual(
            {row["table_name"] for row in tables},
            {
                "documents",
                "document_versions",
                "sections",
                "chunks",
                "embeddings",
                "acl",
                "jobs",
                "query_traces",
            },
        )
        self.assertEqual(len(indexes), 1)
        self.assertEqual(
            {row["name"] for row in settings},
            {"hnsw.iterative_scan", "ivfflat.iterative_scan"},
        )

    def test_jobs_are_claimed_and_leased(self) -> None:
        jobs = PostgresJobStore(self.database_url, "migrations")
        first_id = jobs.enqueue("test", {"id": str(uuid4())})
        second_id = jobs.enqueue("test", {"id": str(uuid4())})

        first = jobs.claim_next()
        second = jobs.claim_next()

        self.assertIsNotNone(first)
        self.assertIsNotNone(second)
        assert first is not None
        assert second is not None
        self.assertEqual({str(first["id"]), str(second["id"])}, {first_id, second_id})
        self.assertEqual(first["status"], "running")
        self.assertEqual(second["status"], "running")
        jobs.fail(str(first["id"]), str(first["lease_token"]), "contract cleanup")
        jobs.fail(str(second["id"]), str(second["lease_token"]), "contract cleanup")


if __name__ == "__main__":
    unittest.main()
