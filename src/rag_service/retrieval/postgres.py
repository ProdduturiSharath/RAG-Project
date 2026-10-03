"""Phase 1 exact local scoring baseline over an authorized Postgres snapshot.

SQL filters active revisions and ACLs before loading any candidate text. The
Phase 2 pipeline will replace the full-snapshot scoring with dense/FTS stages.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import replace

from rag_service.storage.postgres import PostgresDatabase
from rag_service.storage.serialization import chunk_from_payload

from .memory import InMemoryHybridIndex
from .models import RetrievalFilters, ScoredChunk


class PostgresHybridIndex:
    def __init__(
        self,
        database_url: str,
        *,
        embedder_id: str = "hash-v1",
        migrations_path: str = "migrations",
    ) -> None:
        self.database = PostgresDatabase(database_url, migrations_path)
        self.embedder_id = embedder_id

    @property
    def count(self) -> int:
        with self.database.connect() as conn:
            row = conn.execute("""SELECT count(*) AS count FROM chunks c JOIN document_versions v
                ON v.id=c.document_version_id WHERE v.status='active'""").fetchone()
            assert row is not None
            return int(row["count"])

    def search(
        self, dense_vector: Sequence[float], sparse_vector: Mapping[str, float], *,
        top_k: int, alpha: float, filters: RetrievalFilters | None = None,
    ) -> tuple[ScoredChunk, ...]:
        filters = filters or RetrievalFilters()
        with self.database.connect() as conn:
            rows = conn.execute("""SELECT c.payload, e.embedding::text, e.sparse_vector
                FROM chunks c JOIN document_versions v ON v.id=c.document_version_id
                JOIN chunk_embeddings ce ON ce.chunk_id=c.id AND ce.embedder_id=%s
                JOIN embeddings e ON e.content_hash=ce.content_hash AND e.embedder_id=ce.embedder_id
                WHERE v.status='active'
                AND (%s::text IS NULL OR v.product_version=%s)
                AND (cardinality(%s::text[])=0 OR v.document_id=ANY(%s))
                AND EXISTS (SELECT 1 FROM acl a WHERE a.document_version_id=v.id AND
                    (a.is_public OR a.principal=%s OR a.principal='*'
                     OR a.group_name=ANY(%s) OR a.group_name='*'))""",
                                (self.embedder_id, filters.product_version, filters.product_version,
                                 list(filters.document_ids), list(filters.document_ids),
                                 filters.principal, list(filters.groups))).fetchall()
        snapshot = InMemoryHybridIndex()
        for row in rows:
            # ACL was evaluated by SQL from the current ACL rows, not the payload.
            chunk = replace(chunk_from_payload(row["payload"]), access_policy=None)
            snapshot.upsert([chunk], dense_vectors=[json.loads(row["embedding"])],
                            sparse_vectors=[row["sparse_vector"]])
        # Version/ACL already evaluated by SQL; retain only metadata/document filters.
        return snapshot.search(dense_vector, sparse_vector, top_k=top_k, alpha=alpha,
                               filters=replace(filters, product_version=None))
