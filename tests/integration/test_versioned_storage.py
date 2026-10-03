from __future__ import annotations

import unittest
from collections.abc import Sequence
from typing import Any
from uuid import uuid4

from rag_service.domain import AccessPolicy, DocumentSection
from rag_service.ingestion import ChunkingConfig, DeterministicChunker
from rag_service.retrieval import Bm25SparseEncoder, HashEmbeddingEncoder
from rag_service.storage import InMemoryVersionedStore, PostgresVersionedStore
from tests.integration.database import test_database_url


class CountingEmbedder(HashEmbeddingEncoder):
    def __init__(self) -> None:
        super().__init__(dimensions=16)
        self.calls: list[tuple[str, ...]] = []

    def embed(self, texts: Sequence[str]) -> tuple[tuple[float, ...], ...]:
        batch = tuple(texts)
        self.calls.append(batch)
        return super().embed(batch)


def _database_url() -> str | None:
    return test_database_url()


class VersionedStorageContractTests(unittest.TestCase):
    def _store(self, backend: str) -> tuple[Any, CountingEmbedder, str]:
        embedder = CountingEmbedder()
        chunker = DeterministicChunker(
            config=ChunkingConfig(max_tokens=20, overlap_tokens=2, detect_markdown_headings=True)
        )
        if backend == "memory":
            return (
                InMemoryVersionedStore(
                    chunker,
                    embedder=embedder,
                    sparse_encoder=Bm25SparseEncoder(),
                ),
                embedder,
                "memory",
            )
        url = _database_url()
        if url is None:
            self.skipTest("RAG_TEST_DATABASE_URL is not set")
        store = PostgresVersionedStore(
            url,
            chunker,
            embedder=embedder,
            sparse_encoder=Bm25SparseEncoder(),
            migrations_path="migrations",
        )
        store.migrate()
        return store, embedder, f"phase1-test-{uuid4().hex}"

    def test_noop_new_revision_and_delete_contract(self) -> None:
        for backend in ("memory", "postgres"):
            with self.subTest(backend=backend):
                store, embedder, document_id = self._store(backend)
                sections = [DocumentSection(text="The default value is 10.")]
                first = store.ingest(document_id, sections, "pg17")
                calls_after_first = len(embedder.calls)
                same = store.ingest(document_id, sections, "pg17")
                calls_after_same = len(embedder.calls)
                updated = store.ingest(
                    document_id,
                    [DocumentSection(text="The default value is 20.")],
                    "pg17",
                )

                self.assertEqual(first.revision, 1)
                self.assertTrue(same.already_ingested)
                self.assertEqual(same.revision, 1)
                self.assertEqual(calls_after_same, calls_after_first)
                self.assertEqual(updated.revision, 2)
                self.assertIsNotNone(store.active_revision(document_id, "pg17"))
                self.assertEqual(store.delete_document(document_id, "pg17"), 2)
                self.assertIsNone(store.active_revision(document_id, "pg17"))
                self.assertGreaterEqual(len(embedder.calls), 1)

    def test_acl_only_change_does_not_reembed(self) -> None:
        for backend in ("memory", "postgres"):
            with self.subTest(backend=backend):
                store, embedder, document_id = self._store(backend)
                sections = [DocumentSection(text="Only Alice may read this runbook.")]
                first = store.ingest(
                    document_id,
                    sections,
                    "pg17",
                    access_policy=AccessPolicy(principals=("alice",)),
                )
                calls_after_first = len(embedder.calls)
                same_content = store.ingest(
                    document_id,
                    sections,
                    "pg17",
                    access_policy=AccessPolicy(principals=("bob",)),
                )

                self.assertEqual(first.revision, same_content.revision)
                self.assertTrue(same_content.already_ingested)
                self.assertEqual(len(embedder.calls), calls_after_first)
                self.assertEqual(
                    same_content.chunks[0].access_policy,
                    AccessPolicy(principals=("bob",)),
                )

    def test_same_content_across_product_versions_reuses_embedding(self) -> None:
        for backend in ("memory", "postgres"):
            with self.subTest(backend=backend):
                store, embedder, document_id = self._store(backend)
                sections = [DocumentSection(text="max_wal_senders defaults to 10.")]
                store.ingest(document_id, sections, "pg16")
                calls_after_first = len(embedder.calls)
                store.ingest(document_id, sections, "pg17")

                self.assertEqual(len(embedder.calls), calls_after_first)

    def test_failed_revision_keeps_old_active(self) -> None:
        for backend in ("memory", "postgres"):
            with self.subTest(backend=backend):
                store, _, document_id = self._store(backend)
                store.ingest(document_id, [DocumentSection(text="old value")], "pg17")
                with self.assertRaisesRegex(RuntimeError, "injected failure"):
                    store.ingest(
                        document_id,
                        [DocumentSection(text="new value")],
                        "pg17",
                        fail_after="chunks",
                    )

                active = store.active_revision(document_id, "pg17")
                self.assertIsNotNone(active)
                self.assertEqual(active["revision"], 1)

    def test_embedder_and_chunker_changes_create_provenance_revisions(self) -> None:
        database_url = _database_url()
        if database_url is None:
            self.skipTest("RAG_TEST_DATABASE_URL is not set")
        document_id = f"phase1-provenance-{uuid4().hex}"
        sections = [
            DocumentSection(
                text="The unchanged content is deliberately long enough to produce "
                "more than one configured chunk for provenance testing."
            )
        ]
        first_embedder = CountingEmbedder()
        first = PostgresVersionedStore(
            database_url,
            DeterministicChunker(max_tokens=40, overlap_tokens=0),
            embedder=first_embedder,
            sparse_encoder=Bm25SparseEncoder(),
            embedder_id="hash-v1",
            migrations_path="migrations",
        )
        first.migrate()
        first.ingest(document_id, sections, "pg17")
        second = PostgresVersionedStore(
            database_url,
            DeterministicChunker(max_tokens=40, overlap_tokens=0),
            embedder=CountingEmbedder(),
            sparse_encoder=Bm25SparseEncoder(),
            embedder_id="hash-v2",
            migrations_path="migrations",
        )
        second.ingest(document_id, sections, "pg17")
        third = PostgresVersionedStore(
            database_url,
            DeterministicChunker(max_tokens=4, overlap_tokens=1),
            embedder=CountingEmbedder(),
            sparse_encoder=Bm25SparseEncoder(),
            embedder_id="hash-v2",
            migrations_path="migrations",
        )
        third.ingest(document_id, sections, "pg17")

        active = third.active_revision(document_id, "pg17")
        self.assertIsNotNone(active)
        assert active is not None
        self.assertEqual(active["revision"], 3)
        self.assertEqual(active["embedder_id"], "hash-v2")
        self.assertNotEqual(active["chunker_config_hash"], first.chunker_config_hash)


if __name__ == "__main__":
    unittest.main()
