from __future__ import annotations

import os
import unittest
from collections.abc import Sequence
from typing import Any
from uuid import uuid4

from rag_service.domain import AccessPolicy, DocumentSection
from rag_service.ingestion import ChunkingConfig, DeterministicChunker
from rag_service.retrieval import Bm25SparseEncoder, HashEmbeddingEncoder
from rag_service.storage import InMemoryVersionedStore, PostgresVersionedStore


class CountingEmbedder(HashEmbeddingEncoder):
    def __init__(self) -> None:
        super().__init__(dimensions=16)
        self.calls: list[tuple[str, ...]] = []

    def embed(self, texts: Sequence[str]) -> tuple[tuple[float, ...], ...]:
        batch = tuple(texts)
        self.calls.append(batch)
        return super().embed(batch)


def _database_url() -> str | None:
    return os.getenv("RAG_TEST_DATABASE_URL")


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
                same = store.ingest(document_id, sections, "pg17")
                updated = store.ingest(
                    document_id,
                    [DocumentSection(text="The default value is 20.")],
                    "pg17",
                )

                self.assertEqual(first.revision, 1)
                self.assertTrue(same.already_ingested)
                self.assertEqual(same.revision, 1)
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


if __name__ == "__main__":
    unittest.main()
