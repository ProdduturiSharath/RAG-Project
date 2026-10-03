"""Transactional revisions and leased SKIP LOCKED jobs using plain SQL."""

from __future__ import annotations

import hashlib
import json
import uuid
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import replace
from pathlib import Path
from typing import Any

import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from rag_service.domain import (
    AccessPolicy,
    Chunk,
    DocumentIdentity,
    DocumentSection,
    DocumentVersion,
    IngestionResult,
    SourceLocation,
)
from rag_service.ingestion.chunking import DeterministicChunker
from rag_service.ingestion.ports import Embedder, SparseEncoder

from .serialization import (
    VectorPair,
    chunk_to_payload,
    chunker_hash,
    config_hash,
    prepare_document,
    validate_vectors,
)


class PostgresDatabase:
    def __init__(self, database_url: str, migrations_path: str | Path = "migrations") -> None:
        self.database_url = database_url
        self.migrations_path = Path(migrations_path)

    def connect(self) -> psycopg.Connection[dict[str, Any]]:
        return psycopg.connect(self.database_url, row_factory=dict_row)

    def migrate(self) -> None:
        files = sorted(self.migrations_path.glob("*.sql"))
        if not files:
            raise FileNotFoundError(f"No SQL migrations in {self.migrations_path}")
        with self.connect() as conn:
            conn.execute("SELECT pg_advisory_xact_lock(14782930)")
            conn.execute("""CREATE TABLE IF NOT EXISTS schema_migrations (
                version text PRIMARY KEY, applied_at timestamptz NOT NULL DEFAULT now())""")
            conn.execute("ALTER TABLE schema_migrations ADD COLUMN IF NOT EXISTS checksum text")
            for file in files:
                content = file.read_text(encoding="utf-8")
                checksum = hashlib.sha256(content.encode()).hexdigest()
                row = conn.execute("SELECT checksum FROM schema_migrations WHERE version = %s",
                                   (file.stem,)).fetchone()
                if row and row["checksum"]:
                    if row["checksum"] != checksum:
                        raise ValueError(f"Applied migration changed: {file.name}")
                    continue
                conn.execute(content)
                conn.execute("""INSERT INTO schema_migrations(version, checksum) VALUES (%s, %s)
                    ON CONFLICT (version) DO UPDATE SET checksum = EXCLUDED.checksum""",
                             (file.stem, checksum))


class PostgresVersionedStore:
    def __init__(
        self, database_url: str, chunker: DeterministicChunker, *, embedder: Embedder,
        sparse_encoder: SparseEncoder, embedder_id: str = "hash-v1",
        parser_config_hash: str | None = None, batch_size: int = 64,
        migrations_path: str | Path = "migrations",
    ) -> None:
        if not embedder_id.strip() or batch_size < 1:
            raise ValueError("embedder_id and positive batch_size required")
        self.database = PostgresDatabase(database_url, migrations_path)
        self.chunker = chunker
        self.embedder = embedder
        self.sparse_encoder = sparse_encoder
        self.embedder_id = embedder_id
        self.parser_config_hash = parser_config_hash or config_hash({"parser": "sections-v2"})
        self.batch_size = batch_size

    @property
    def chunker_config_hash(self) -> str:
        return chunker_hash(self.chunker)

    def migrate(self) -> None:
        self.database.migrate()

    def ingest(
        self, document: DocumentIdentity | str,
        sections: Iterable[DocumentSection | Mapping[str, Any]] | str,
        version: DocumentVersion | str | None = None, *, content_hash: str | None = None,
        source: SourceLocation | None = None, access_policy: AccessPolicy | None = None,
        skip_unchanged: bool = True,
        job_id: str | None = None,
        lease_token: str | None = None,
        fail_after: str | None = None,
    ) -> IngestionResult:
        prepared = prepare_document(self.chunker, document, sections, version,
                                    content_hash, source, access_policy)
        doc_id, product_version = prepared.identity.document_id, prepared.version
        vectors = self._prepare_embeddings(prepared.chunks)
        with self.database.connect() as conn:
            if job_id:
                job = conn.execute("SELECT status, lease_token FROM jobs WHERE id=%s FOR UPDATE",
                                   (job_id,)).fetchone()
                if not job or job["status"] != "running" or str(job["lease_token"]) != lease_token:
                    raise ValueError("job lease expired or job cancelled")
            # The document row serializes first ingestion, update, ACL and delete.
            conn.execute("""INSERT INTO documents(document_id, title, source_uri, metadata)
                VALUES (%s,%s,%s,%s) ON CONFLICT(document_id) DO UPDATE SET
                title=EXCLUDED.title, source_uri=EXCLUDED.source_uri,
                metadata=EXCLUDED.metadata, updated_at=now()""",
                         (doc_id, prepared.identity.title,
                          prepared.source.stable_uri if prepared.source else None,
                          Jsonb(dict(prepared.identity.metadata))))
            active = conn.execute("""SELECT * FROM document_versions WHERE document_id=%s
                AND product_version=%s AND status='active'""", (doc_id, product_version)).fetchone()
            unchanged = bool(skip_unchanged and active
                             and active["content_hash"] == prepared.content_hash
                             and active["parser_config_hash"] == self.parser_config_hash
                             and active["chunker_config_hash"] == self.chunker_config_hash
                             and active["embedder_id"] == self.embedder_id)
            if unchanged and active:
                version_id, revision = active["id"], active["revision"]
                chunks = tuple(replace(c, revision=revision) for c in prepared.chunks)
            else:
                row = conn.execute("""SELECT COALESCE(MAX(revision),0)+1 AS revision
                    FROM document_versions WHERE document_id=%s AND product_version=%s""",
                                   (doc_id, product_version)).fetchone()
                assert row is not None
                revision = row["revision"]
                chunks = tuple(replace(c, revision=revision) for c in prepared.chunks)
                row = conn.execute("""INSERT INTO document_versions(document_id, product_version,
                    revision, content_hash, status, parser_config_hash, chunker_config_hash,
                    embedder_id, source_uri) VALUES (%s,%s,%s,%s,'building',%s,%s,%s,%s)
                    RETURNING id""",
                                   (doc_id, product_version, revision, prepared.content_hash,
                                    self.parser_config_hash, self.chunker_config_hash,
                                    self.embedder_id,
                                    prepared.source.stable_uri if prepared.source else None)
                                   ).fetchone()
                assert row is not None
                version_id = row["id"]
                self._insert_chunks(conn, version_id, chunks)
                if fail_after == "chunks":
                    raise RuntimeError("injected failure after chunk insertion")
                self._insert_embeddings(conn, vectors)
                conn.execute("""INSERT INTO chunk_embeddings
                    (document_version_id, chunk_id, content_hash, embedder_id)
                    SELECT document_version_id, id, content_hash, %s FROM chunks
                    WHERE document_version_id=%s""", (self.embedder_id, version_id))
                conn.execute("""UPDATE document_versions SET status='superseded'
                    WHERE document_id=%s AND product_version=%s AND status='active'""",
                             (doc_id, product_version))
                conn.execute("UPDATE document_versions SET status='active', activated_at=now()"
                             " WHERE id=%s", (version_id,))
            self._replace_acl(conn, version_id, prepared.policy)
            result = IngestionResult(
                doc_id, product_version, prepared.content_hash, chunks=chunks,
                ingestion_id=f"revision-{version_id}", source=prepared.source,
                access_policy=prepared.policy, already_ingested=unchanged, revision=revision,
                dense_vectors=tuple(vectors[c.content_hash or ""][0] for c in chunks),
                sparse_vectors=tuple(vectors[c.content_hash or ""][1] for c in chunks),
            )
            if job_id:
                conn.execute("""UPDATE jobs SET status='succeeded', finished_at=now(), result=%s,
                    payload='{}'::jsonb, locked_at=NULL WHERE id=%s""",
                             (Jsonb({"document_id": doc_id, "product_version": product_version,
                                     "revision": revision, "chunk_count": result.chunk_count,
                                     "already_ingested": unchanged}), job_id))
        return result

    def active_revision(self, document_id: str, product_version: str) -> dict[str, Any] | None:
        with self.database.connect() as conn:
            return conn.execute("""SELECT * FROM document_versions WHERE document_id=%s
                AND product_version=%s AND status='active'""",
                                (document_id, product_version)).fetchone()

    def delete_document(self, document_id: str, product_version: str | None = None) -> int:
        with self.database.connect() as conn:
            # Cancel outstanding jobs first, using the same lock order as activation.
            conn.execute("""UPDATE jobs SET status='failed', error='document deleted',
                payload='{}'::jsonb, finished_at=now(), lease_token=NULL
                WHERE payload->>'document_id'=%s AND (%s::text IS NULL
                OR COALESCE(payload->>'product_version',payload->>'version')=%s)
                AND status IN ('queued','running')""",
                (document_id, product_version, product_version),
            )
            conn.execute("SELECT document_id FROM documents WHERE document_id=%s FOR UPDATE",
                         (document_id,))
            rows = conn.execute("""UPDATE document_versions SET status='deleted', deleted_at=now()
                WHERE document_id=%s AND (%s::text IS NULL OR product_version=%s)
                AND status<>'deleted' RETURNING id""",
                                (document_id, product_version, product_version)).fetchall()
            ids = [row["id"] for row in rows]
            conn.execute("DELETE FROM sections WHERE document_version_id=ANY(%s)", (ids,))
            conn.execute("DELETE FROM acl WHERE document_version_id=ANY(%s)", (ids,))
            conn.execute("""DELETE FROM embeddings e WHERE NOT EXISTS
                (SELECT 1 FROM chunk_embeddings ce WHERE ce.content_hash=e.content_hash
                 AND ce.embedder_id=e.embedder_id)""")
            return len(ids)

    def _prepare_embeddings(self, chunks: Sequence[Chunk]) -> dict[str, VectorPair]:
        unique = {c.content_hash or "": c for c in chunks}
        with self.database.connect() as conn:
            rows = conn.execute("""SELECT content_hash, embedding::text, sparse_vector
                FROM embeddings WHERE embedder_id=%s AND content_hash=ANY(%s)""",
                                (self.embedder_id, list(unique))).fetchall()
        vectors: dict[str, VectorPair] = {
            row["content_hash"]: (tuple(json.loads(row["embedding"])), row["sparse_vector"])
            for row in rows
        }
        missing = [key for key in unique if key not in vectors]
        for start in range(0, len(missing), self.batch_size):
            keys = missing[start:start + self.batch_size]
            chunks = tuple(unique[key] for key in keys)
            embed_chunks = getattr(self.embedder, "embed_chunks", None)
            dense = embed_chunks(chunks) if embed_chunks is not None else self.embedder.embed(
                tuple(chunk.text for chunk in chunks)
            )
            values = validate_vectors(
                dense,
                self.sparse_encoder.encode(tuple(chunk.text for chunk in chunks)),
                len(keys),
            )
            vectors.update(zip(keys, values, strict=True))
        return vectors

    def _insert_embeddings(
        self, conn: psycopg.Connection[Any], vectors: Mapping[str, VectorPair]
    ) -> None:
        for key, (dense, sparse) in vectors.items():
            conn.execute("""INSERT INTO embeddings(content_hash,embedder_id,embedding,
                sparse_vector,dimensions) VALUES (%s,%s,%s::vector,%s,%s)
                ON CONFLICT(content_hash,embedder_id) DO NOTHING""",
                         (key, self.embedder_id, json.dumps(dense), Jsonb(sparse), len(dense)))

    @staticmethod
    def _insert_chunks(
        conn: psycopg.Connection[Any], version_id: int, chunks: Sequence[Chunk]
    ) -> None:
        sections: dict[str, int] = {}
        paths: dict[tuple[str, ...], int] = {}
        for chunk in chunks:
            key = chunk.section_id or chunk.chunk_id
            if key not in sections:
                row = conn.execute("""INSERT INTO sections(document_version_id, section_key,
                    heading_path, lineage_key, text, page, metadata, ordinal)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id""",
                                   (version_id, key, Jsonb(list(chunk.section_path)),
                                    chunk.lineage_key, chunk.parent_text or chunk.text,
                                    chunk.page_number, Jsonb(dict(chunk.metadata)), chunk.ordinal)
                                   ).fetchone()
                assert row is not None
                sections[key] = row["id"]
                paths[chunk.section_path] = row["id"]
            conn.execute("""INSERT INTO chunks(document_version_id,section_id,chunk_key,
                parent_key,kind,text,token_count,page,content_hash,source_uri,metadata,payload)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                         (version_id, sections[key], chunk.chunk_id, chunk.parent_id, chunk.kind,
                          chunk.text, len(chunk.text.split()), chunk.page_number,
                          chunk.content_hash,
                          chunk.source.stable_uri if chunk.source else None,
                          Jsonb(dict(chunk.metadata)), Jsonb(chunk_to_payload(chunk))))
        for path, section_id in paths.items():
            if path and path[:-1] in paths:
                conn.execute("UPDATE sections SET parent_id=%s WHERE id=%s",
                             (paths[path[:-1]], section_id))
        conn.execute("""UPDATE chunks child SET parent_id=parent.id FROM chunks parent
            WHERE child.document_version_id=%s AND parent.document_version_id=%s
            AND child.parent_key=parent.chunk_key""", (version_id, version_id))

    @staticmethod
    def _replace_acl(
        conn: psycopg.Connection[Any], version_id: int, policy: AccessPolicy | None
    ) -> None:
        conn.execute("DELETE FROM acl WHERE document_version_id=%s", (version_id,))
        if policy is None or policy.public:
            conn.execute("INSERT INTO acl(document_version_id,is_public) VALUES (%s,true)",
                         (version_id,))
        else:
            conn.execute("INSERT INTO acl(document_version_id) VALUES (%s)", (version_id,))
            for principal in policy.principals:
                conn.execute("INSERT INTO acl(document_version_id,principal) VALUES (%s,%s)",
                             (version_id, principal))
            for group in policy.groups:
                conn.execute("INSERT INTO acl(document_version_id,group_name) VALUES (%s,%s)",
                             (version_id, group))


class PostgresJobStore:
    def __init__(self, database_url: str, migrations_path: str | Path = "migrations") -> None:
        self.database = PostgresDatabase(database_url, migrations_path)

    def enqueue(self, kind: str, payload: Mapping[str, Any]) -> str:
        job_id = str(uuid.uuid4())
        with self.database.connect() as conn:
            conn.execute("INSERT INTO jobs(id,kind,payload,status) VALUES (%s,%s,%s,'queued')",
                         (job_id, kind, Jsonb(dict(payload))))
        return job_id

    def get(self, job_id: str) -> dict[str, Any] | None:
        with self.database.connect() as conn:
            return conn.execute("SELECT * FROM jobs WHERE id=%s", (job_id,)).fetchone()

    def claim_next(self, kind: str | None = None) -> dict[str, Any] | None:
        with self.database.connect() as conn:
            conn.execute("""UPDATE jobs SET status='queued', lease_token=NULL
                WHERE status='running' AND locked_at < now()-interval '5 minutes'""")
            if kind is None:
                return conn.execute("""UPDATE jobs SET status='running', attempts=attempts+1,
                    started_at=now(), locked_at=now(), lease_token=%s WHERE id=(
                        SELECT id FROM jobs WHERE status='queued' ORDER BY created_at,id
                        FOR UPDATE SKIP LOCKED LIMIT 1) RETURNING *""", (uuid.uuid4(),)).fetchone()
            return conn.execute("""UPDATE jobs SET status='running', attempts=attempts+1,
                started_at=now(), locked_at=now(), lease_token=%s WHERE id=(
                    SELECT id FROM jobs WHERE status='queued' AND kind=%s
                    ORDER BY created_at,id FOR UPDATE SKIP LOCKED LIMIT 1) RETURNING *""",
                                (uuid.uuid4(), kind)).fetchone()

    def fail(self, job_id: str, lease_token: str, error: str) -> None:
        with self.database.connect() as conn:
            conn.execute("""UPDATE jobs SET status='failed', error=%s, finished_at=now(),
                payload='{}'::jsonb, locked_at=NULL WHERE id=%s AND lease_token=%s
                AND status='running'""", (error, job_id, lease_token))
