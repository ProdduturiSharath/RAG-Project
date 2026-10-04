"""Phase 1 exact local scoring baseline over an authorized Postgres snapshot.

SQL filters active revisions and ACLs before loading any candidate text. The
Phase 2 pipeline will replace the full-snapshot scoring with dense/FTS stages.
"""

from __future__ import annotations

import json
import re
from collections.abc import Mapping, Sequence
from dataclasses import replace
from typing import Any

from psycopg.types.json import Jsonb

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

    def available_versions(self, filters: RetrievalFilters) -> dict[str, tuple[str, ...]]:
        where, params = self._scope_where(filters)
        query = f"""SELECT v.document_id, v.product_version
            FROM document_versions v
            WHERE v.status='active' AND {where}
            ORDER BY v.document_id, v.product_version"""
        with self.database.connect() as conn:
            rows = conn.execute(query, params).fetchall()
        versions: dict[str, list[str]] = {}
        for row in rows:
            versions.setdefault(row["document_id"], []).append(row["product_version"])
        return {key: tuple(value) for key, value in versions.items()}

    def dense_search(self, dense_vector: Sequence[float], *, top_k: int,
                     filters: RetrievalFilters) -> tuple[ScoredChunk, ...]:
        if not dense_vector:
            return ()
        vector = json.dumps([float(value) for value in dense_vector])
        where, params = self._scope_where(filters)
        query = f"""SELECT c.payload, e.embedding <=> %s::vector AS distance
            FROM chunks c
            JOIN document_versions v ON v.id=c.document_version_id
            JOIN chunk_embeddings ce ON ce.chunk_id=c.id AND ce.embedder_id=%s
            JOIN embeddings e ON e.content_hash=ce.content_hash AND e.embedder_id=ce.embedder_id
            WHERE v.status='active' AND {where}
            ORDER BY e.embedding <=> %s::vector
            LIMIT %s"""
        values = (vector, self.embedder_id, *params, vector, top_k)
        with self.database.connect() as conn:
            conn.execute("SET LOCAL hnsw.iterative_scan = strict_order")
            rows = conn.execute(query, values).fetchall()
        return tuple(
            ScoredChunk(
                chunk=replace(chunk_from_payload(row["payload"]), access_policy=None),
                dense_score=1.0 - float(row["distance"]),
                rank=rank,
            )
            for rank, row in enumerate(rows, 1)
        )

    def sparse_search(self, query_text: str, *, top_k: int,
                      filters: RetrievalFilters) -> tuple[ScoredChunk, ...]:
        normalized = re.sub(r"[_./-]", " ", query_text)
        where, params = self._scope_where(filters)
        query = f"""WITH terms AS (
                SELECT plainto_tsquery('simple', %s) AS plain,
                       plainto_tsquery('simple', %s) AS identifiers
            )
            SELECT c.payload,
                   greatest(ts_rank_cd(c.search_vector, terms.plain),
                            ts_rank_cd(c.identifier_vector, terms.identifiers)) AS score
            FROM chunks c
            JOIN document_versions v ON v.id=c.document_version_id
            CROSS JOIN terms
            WHERE v.status='active' AND {where}
              AND (c.search_vector @@ terms.plain OR c.identifier_vector @@ terms.identifiers)
            ORDER BY score DESC, c.id
            LIMIT %s"""
        with self.database.connect() as conn:
            rows = conn.execute(query, (query_text, normalized, *params, top_k)).fetchall()
        return tuple(
            ScoredChunk(
                chunk=replace(chunk_from_payload(row["payload"]), access_policy=None),
                sparse_score=float(row["score"]),
                rank=rank,
            )
            for rank, row in enumerate(rows, 1)
        )

    def expand_parents(self, matches: Sequence[ScoredChunk], *,
                       filters: RetrievalFilters) -> tuple[ScoredChunk, ...]:
        parent_keys = tuple(dict.fromkeys(
            match.chunk.parent_id for match in matches if match.chunk.parent_id
        ))
        if not parent_keys:
            return tuple(matches)
        where, params = self._scope_where(filters)
        query = f"""SELECT c.payload FROM chunks c
            JOIN document_versions v ON v.id=c.document_version_id
            WHERE v.status='active' AND c.chunk_key=ANY(%s) AND {where}"""
        with self.database.connect() as conn:
            rows = conn.execute(query, (list(parent_keys), *params)).fetchall()
        parents = {
            chunk_from_payload(row["payload"]).chunk_id: chunk_from_payload(row["payload"])
            for row in rows
        }
        expanded: list[ScoredChunk] = []
        seen: set[str] = set()
        for match in matches:
            if match.chunk.chunk_id not in seen:
                expanded.append(match)
                seen.add(match.chunk.chunk_id)
            parent = parents.get(match.chunk.parent_id or "")
            if parent is not None and parent.chunk_id not in seen:
                expanded.append(
                    replace(match, chunk=parent, hybrid_score=match.hybrid_score * 0.95)
                )
                seen.add(parent.chunk_id)
        return tuple(expanded)

    def save_trace(self, trace_id: str, query: str, filters: RetrievalFilters,
                   stages: Sequence[dict[str, Any]]) -> None:
        with self.database.connect() as conn:
            conn.execute("""INSERT INTO query_traces
                (id, query, requester, product_version, stages)
                VALUES (%s,%s,%s,%s,%s)
                ON CONFLICT (id) DO UPDATE SET stages=EXCLUDED.stages""",
                         (trace_id, query, filters.principal, filters.product_version,
                          Jsonb(list(stages))))

    def _scope_where(self, filters: RetrievalFilters) -> tuple[str, list[Any]]:
        clauses = ["TRUE"]
        params: list[Any] = []
        if filters.document_ids:
            clauses.append("v.document_id=ANY(%s)")
            params.append(list(filters.document_ids))
        if filters.product_version is not None:
            clauses.append("v.product_version=%s")
            params.append(filters.product_version)
        if filters.scopes is not None:
            if not filters.scopes:
                clauses.append("FALSE")
            else:
                scopes = []
                for document_id, version in filters.scopes:
                    scopes.append("(v.document_id=%s AND v.product_version=%s)")
                    params.extend((document_id, version))
                clauses.append("(" + " OR ".join(scopes) + ")")
        acl = ["a.is_public", "a.principal=%s", "a.principal='*'"]
        params.append(filters.principal)
        if filters.groups:
            acl.append("a.group_name=ANY(%s)")
            params.append(list(filters.groups))
        acl.append("a.group_name='*'")
        clauses.append("EXISTS (SELECT 1 FROM acl a WHERE a.document_version_id=v.id AND ("
                       + " OR ".join(acl) + "))")
        return " AND ".join(clauses), params
