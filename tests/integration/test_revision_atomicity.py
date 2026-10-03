from collections.abc import Sequence
from concurrent.futures import ThreadPoolExecutor
from threading import Event
from typing import Any
from unittest.mock import patch
from uuid import uuid4

import psycopg
import pytest

from rag_service.domain import AccessPolicy, Chunk, DocumentSection
from rag_service.ingestion import DeterministicChunker
from rag_service.retrieval import Bm25SparseEncoder, PostgresHybridIndex, RetrievalFilters
from rag_service.storage import PostgresVersionedStore
from tests.integration.database import test_database_url
from tests.integration.test_versioned_storage import CountingEmbedder


@pytest.fixture
def store() -> PostgresVersionedStore:
    url = test_database_url()
    if url is None:
        pytest.skip("RAG_TEST_DATABASE_URL is not set")
    result = PostgresVersionedStore(
        url, DeterministicChunker(max_tokens=20, overlap_tokens=0),
        embedder=CountingEmbedder(), sparse_encoder=Bm25SparseEncoder(),
    )
    result.migrate()
    return result


def sections(label: str) -> list[DocumentSection]:
    return [DocumentSection(text=f"{label} chunk {i}", heading=f"Section {i}", level=1)
            for i in range(4)]


def visible(store: PostgresVersionedStore, document_id: str) -> set[tuple[int, str]]:
    index = PostgresHybridIndex(store.database.database_url)
    matches = index.search(
        [0.0] * 16, {}, top_k=100, alpha=0.5,
        filters=RetrievalFilters(
            document_ids=(document_id,), product_version="pg17", principal="alice",
        ),
    )
    return {(match.chunk.revision, match.chunk.text) for match in matches}


def test_failure_halfway_through_chunks_preserves_entire_old_revision(
    store: PostgresVersionedStore,
) -> None:
    document_id = uuid4().hex
    old = store.ingest(document_id, sections("old"), "pg17",
                       access_policy=AccessPolicy(principals=("alice",)))
    original = store._insert_chunks

    def fail_halfway(conn: psycopg.Connection[Any], version_id: int,
                     chunks: Sequence[Chunk]) -> None:
        original(conn, version_id, chunks[:len(chunks) // 2])
        row = conn.execute("SELECT count(*) AS n FROM chunks WHERE document_version_id=%s",
                           (version_id,)).fetchone()
        assert row is not None and row["n"] == 2
        raise RuntimeError("injected failure halfway through chunk insertion")

    with patch.object(store, "_insert_chunks", side_effect=fail_halfway):
        with pytest.raises(RuntimeError, match="halfway"):
            store.ingest(document_id, sections("new"), "pg17",
                         access_policy=AccessPolicy(principals=("bob",)))

    assert visible(store, document_id) == {(1, c.text) for c in old.chunks}
    with store.database.connect() as conn:
        rows = conn.execute("SELECT revision, status FROM document_versions WHERE document_id=%s",
                            (document_id,)).fetchall()
        assert rows == [{"revision": 1, "status": "active"}]
        rows = conn.execute("""SELECT c.text FROM chunks c JOIN document_versions v
            ON v.id=c.document_version_id WHERE v.document_id=%s""", (document_id,)).fetchall()
        assert {r["text"] for r in rows} == {c.text for c in old.chunks}
        rows = conn.execute("""SELECT a.principal FROM acl a JOIN document_versions v
            ON v.id=a.document_version_id WHERE v.document_id=%s""", (document_id,)).fetchall()
        assert {r["principal"] for r in rows} == {None, "alice"}


def test_reader_sees_only_complete_revisions_during_update(store: PostgresVersionedStore) -> None:
    document_id = uuid4().hex
    old = store.ingest(document_id, sections("old"), "pg17")
    old_snapshot = {(1, c.text) for c in old.chunks}
    halfway, continue_chunks, activated, allow_commit = (Event() for _ in range(4))
    original_chunks, original_acl = store._insert_chunks, store._replace_acl

    def pause_halfway(conn: psycopg.Connection[Any], version_id: int,
                      chunks: Sequence[Chunk]) -> None:
        original_chunks(conn, version_id, chunks[:2])
        halfway.set()
        assert continue_chunks.wait(10), "reader did not release chunk insertion"
        original_chunks(conn, version_id, chunks[2:])

    def pause_before_commit(conn: psycopg.Connection[Any], version_id: int,
                            policy: AccessPolicy | None) -> None:
        original_acl(conn, version_id, policy)
        activated.set()
        assert allow_commit.wait(10), "reader did not release commit"

    with patch.object(store, "_insert_chunks", side_effect=pause_halfway), \
            patch.object(store, "_replace_acl", side_effect=pause_before_commit), \
            ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(store.ingest, document_id, sections("new"), "pg17")
        try:
            assert halfway.wait(10), "writer never inserted first half"
            assert visible(store, document_id) == old_snapshot
            continue_chunks.set()
            if not activated.wait(10):
                future.result(timeout=1)  # expose the actual writer failure
                pytest.fail("writer never activated replacement")
            # Supersession and activation have run, but have not committed.
            assert visible(store, document_id) == old_snapshot
        finally:
            continue_chunks.set()
            allow_commit.set()
        new = future.result(timeout=10)
    assert visible(store, document_id) == {(2, c.text) for c in new.chunks}


def test_database_rejects_second_active_revision(store: PostgresVersionedStore) -> None:
    document_id = uuid4().hex
    store.ingest(document_id, sections("old"), "pg17")
    with store.database.connect() as conn:
        with pytest.raises(psycopg.errors.UniqueViolation, match="document_versions_one_active"):
            with conn.transaction():
                conn.execute("""INSERT INTO document_versions
                    (document_id, product_version, revision, content_hash, status,
                     parser_config_hash, chunker_config_hash, embedder_id)
                    SELECT document_id, product_version, revision+1, content_hash, 'active',
                           parser_config_hash, chunker_config_hash, embedder_id
                    FROM document_versions WHERE document_id=%s AND status='active'""",
                             (document_id,))


def test_simultaneous_same_document_ingestions_have_one_active_revision(
    store: PostgresVersionedStore,
) -> None:
    document_id = uuid4().hex
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [
            pool.submit(store.ingest, document_id, sections("same"), "pg17")
            for _ in range(2)
        ]
        results = [future.result(timeout=10) for future in futures]

    assert {result.revision for result in results} == {1}
    with store.database.connect() as conn:
        rows = conn.execute("""SELECT revision, status FROM document_versions
            WHERE document_id=%s AND product_version='pg17'""", (document_id,)).fetchall()
    assert rows == [{"revision": 1, "status": "active"}]
