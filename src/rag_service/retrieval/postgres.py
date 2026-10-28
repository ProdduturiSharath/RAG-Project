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

from rag_service.domain import AccessPolicy
from rag_service.storage.postgres import PostgresDatabase
from rag_service.storage.serialization import chunk_from_payload

from .memory import InMemoryHybridIndex
from .models import RetrievalFilters, ScoredChunk

_TSQUERY_TERM_RE = re.compile(r"[a-z0-9]+(?:[_./-][a-z0-9]+)*", re.IGNORECASE)
_QUESTION_STOPWORDS = frozenset(
    "a an the is are was were be been being do does did what which who whose when where "
    "why how in on at to of for from by with without and or as it its this that these "
    "those can could would should may might must will shall version".split()
)
_SPARSE_IGNORED_TERMS = frozenset(("postgresql", "version"))
_SPARSE_MAX_DOCUMENT_SHARE = 0.05
_SPARSE_STATS_CACHE: dict[str, tuple[int, dict[str, int]]] = {}


def _query_terms(value: str) -> tuple[str, ...]:
    return tuple(dict.fromkeys(_TSQUERY_TERM_RE.findall(value.casefold())))


def _ignored_sparse_term(term: str) -> bool:
    return bool(
        term in _SPARSE_IGNORED_TERMS
        or term in _QUESTION_STOPWORDS
        or term.isdigit()
        or re.fullmatch(r"(?:pg|postgresql|v)[-_.]?\d+(?:[-_.]\d+)*", term)
    )


def _keep_sparse_term(
    term: str,
    document_frequencies: Mapping[str, int],
    document_count: int,
    max_document_share: float,
) -> bool:
    if _ignored_sparse_term(term):
        return False
    # Compound spellings are identifier evidence even when a component such as
    # "limit" is common in prose.
    if any(separator in term for separator in "_./-"):
        return True
    if not document_count:
        return True
    return document_frequencies.get(term, 0) / document_count <= max_document_share


def _filtered_sparse_query_texts(
    query_text: str,
    document_frequencies: Mapping[str, int],
    document_count: int,
    max_document_share: float = _SPARSE_MAX_DOCUMENT_SHARE,
) -> tuple[str, str, tuple[str, ...]]:
    normalized = re.sub(r"[_./-]", " ", query_text)
    plain_terms = _query_terms(query_text)
    identifier_terms = _query_terms(normalized)
    dropped: list[str] = []

    def kept(terms: Sequence[str]) -> list[str]:
        output: list[str] = []
        for term in terms:
            if _keep_sparse_term(term, document_frequencies, document_count, max_document_share):
                output.append(term)
            else:
                dropped.append(term)
        return output

    plain = kept(plain_terms)
    identifiers = kept(identifier_terms)
    for term in plain_terms:
        if any(separator in term for separator in "_./-") and term not in identifiers:
            identifiers.append(term)
    return (
        " | ".join(f"'{term}'" for term in plain),
        " | ".join(f"'{term}'" for term in dict.fromkeys(identifiers)),
        tuple(dict.fromkeys(dropped)),
    )


def sparse_query_texts(query_text: str) -> tuple[str, str]:
    """Build safe OR queries for prose and punctuation-normalized identifiers.

    ``plainto_tsquery`` joins every parsed token with AND.  A natural-language
    question therefore asks one chunk to contain words such as ``what``,
    ``does``, and ``set`` at the same time.  OR terms preserve rank-based FTS
    retrieval while the second query continues to target identifier components.
    Terms are quoted literals, not user-supplied tsquery syntax. Within one
    identifier, the Postgres parser retains its normal compound-token semantics;
    unrelated question terms are joined by OR. Stopword removal is fixed and
    query-only; existing simple-dictionary indexes need no migration.
    """

    normalized = re.sub(r"[_./-]", " ", query_text)

    def build(value: str) -> str:
        terms = _query_terms(value)
        return " | ".join(f"'{term}'" for term in terms if term not in _QUESTION_STOPWORDS)

    return build(query_text), build(normalized)


def filter_sparse_terms(
    query_text: str,
    document_frequencies: Mapping[str, int],
    document_count: int,
    max_document_share: float = _SPARSE_MAX_DOCUMENT_SHARE,
) -> tuple[str, str]:
    """Return filtered prose and identifier OR queries for the Postgres path."""

    plain, identifiers, _ = _filtered_sparse_query_texts(
        query_text, document_frequencies, document_count, max_document_share
    )
    return plain, identifiers


class PostgresHybridIndex:
    def __init__(
        self,
        database_url: str,
        *,
        embedder_id: str = "hash-v1",
        migrations_path: str = "migrations",
        connect_timeout_seconds: int = 5,
        statement_timeout_ms: int = 30_000,
    ) -> None:
        self.database = PostgresDatabase(
            database_url,
            migrations_path,
            connect_timeout_seconds=connect_timeout_seconds,
            statement_timeout_ms=statement_timeout_ms,
        )
        self.embedder_id = embedder_id

    @property
    def count(self) -> int:
        with self.database.connect() as conn:
            row = conn.execute("""SELECT count(*) AS count FROM chunks c JOIN document_versions v
                ON v.id=c.document_version_id WHERE v.status='active'""").fetchone()
            assert row is not None
            return int(row["count"])

    @property
    def public_count(self) -> int:
        with self.database.connect() as conn:
            row = conn.execute(
                """SELECT count(*) AS count FROM chunks c
                JOIN document_versions v ON v.id=c.document_version_id
                WHERE v.status='active' AND EXISTS (
                    SELECT 1 FROM acl a WHERE a.document_version_id=v.id AND a.is_public)"""
            ).fetchone()
            assert row is not None
            return int(row["count"])

    def search(
        self,
        dense_vector: Sequence[float],
        sparse_vector: Mapping[str, float],
        *,
        top_k: int,
        alpha: float,
        filters: RetrievalFilters | None = None,
    ) -> tuple[ScoredChunk, ...]:
        filters = filters or RetrievalFilters()
        with self.database.connect() as conn:
            rows = conn.execute(
                """SELECT c.payload, e.embedding::text, e.sparse_vector
                FROM chunks c JOIN document_versions v ON v.id=c.document_version_id
                JOIN chunk_embeddings ce ON ce.chunk_id=c.id AND ce.embedder_id=%s
                JOIN embeddings e ON e.content_hash=ce.content_hash AND e.embedder_id=ce.embedder_id
                WHERE v.status='active'
                AND (%s::text IS NULL OR v.product_version=%s)
                AND (cardinality(%s::text[])=0 OR v.document_id=ANY(%s))
                AND EXISTS (SELECT 1 FROM acl a WHERE a.document_version_id=v.id AND
                    (a.is_public OR a.principal=%s OR a.principal='*'
                     OR a.group_name=ANY(%s) OR a.group_name='*'))""",
                (
                    self.embedder_id,
                    filters.product_version,
                    filters.product_version,
                    list(filters.document_ids),
                    list(filters.document_ids),
                    filters.principal,
                    list(filters.groups),
                ),
            ).fetchall()
        snapshot = InMemoryHybridIndex()
        for row in rows:
            # ACL was evaluated by SQL from the current ACL rows, not the payload.
            chunk = replace(chunk_from_payload(row["payload"]), access_policy=None)
            snapshot.upsert(
                [chunk],
                dense_vectors=[json.loads(row["embedding"])],
                sparse_vectors=[row["sparse_vector"]],
            )
        # Version/ACL already evaluated by SQL; retain only metadata/document filters.
        return snapshot.search(
            dense_vector,
            sparse_vector,
            top_k=top_k,
            alpha=alpha,
            filters=replace(filters, product_version=None),
        )

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

    def dense_search(
        self, dense_vector: Sequence[float], *, top_k: int, filters: RetrievalFilters
    ) -> tuple[ScoredChunk, ...]:
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
            ORDER BY e.embedding <=> %s::vector, c.chunk_key
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

    def sparse_search(
        self, query_text: str, *, top_k: int, filters: RetrievalFilters
    ) -> tuple[ScoredChunk, ...]:
        with self.database.connect() as conn:
            document_stats = self._document_frequencies(conn)
            terms, source, params = self._sparse_sql(
                query_text, filters, document_stats=document_stats
            )
            query = f"""{terms} SELECT c.payload,
                   greatest(ts_rank_cd(c.search_vector, terms.plain),
                             ts_rank_cd(c.identifier_vector, terms.identifiers)) AS score
            {source}
            ORDER BY score DESC, c.id
            LIMIT %s"""
            rows = conn.execute(query, (*params, top_k)).fetchall()
        return tuple(
            ScoredChunk(
                chunk=replace(chunk_from_payload(row["payload"]), access_policy=None),
                sparse_score=float(row["score"]),
                rank=rank,
            )
            for rank, row in enumerate(rows, 1)
        )

    def _sparse_sql(
        self,
        query_text: str,
        filters: RetrievalFilters,
        *,
        document_stats: tuple[int, Mapping[str, int]] | None = None,
    ) -> tuple[str, str, tuple[Any, ...]]:
        if document_stats is None:
            plain_query, identifier_query = sparse_query_texts(query_text)
        else:
            document_count, document_frequencies = document_stats
            plain_query, identifier_query, _ = _filtered_sparse_query_texts(
                query_text, document_frequencies, document_count
            )
        where, params = self._scope_where(filters)
        terms = """WITH terms AS (
            SELECT to_tsquery('simple', %s) AS plain,
                   to_tsquery('simple', %s) AS identifiers
        )"""
        common = f"""FROM chunks c
            JOIN document_versions v ON v.id=c.document_version_id
            CROSS JOIN terms
            WHERE v.status='active' AND {where}
              AND (c.search_vector @@ terms.plain
                   OR c.identifier_vector @@ terms.identifiers)"""
        return terms, common, (plain_query, identifier_query, *params)

    def _document_frequencies(self, conn: Any) -> tuple[int, dict[str, int]]:
        cache_key = self.database.database_url
        cached = _SPARSE_STATS_CACHE.get(cache_key)
        if cached is not None:
            return cached
        count_row = conn.execute("""
            SELECT count(*) AS count
            FROM chunks c JOIN document_versions v ON v.id=c.document_version_id
            WHERE v.status='active'
        """).fetchone()
        rows = conn.execute("""
            SELECT term, count(*) AS df
            FROM (
                SELECT c.id, token.lexeme AS term
                FROM chunks c
                JOIN document_versions v ON v.id=c.document_version_id
                CROSS JOIN LATERAL unnest(tsvector_to_array(c.search_vector)) AS token(lexeme)
                WHERE v.status='active'
                UNION
                SELECT c.id, token.lexeme AS term
                FROM chunks c
                JOIN document_versions v ON v.id=c.document_version_id
                CROSS JOIN LATERAL unnest(tsvector_to_array(c.identifier_vector)) AS token(lexeme)
                WHERE v.status='active'
            ) AS terms
            GROUP BY term
        """).fetchall()
        stats = (
            int(count_row["count"]) if count_row else 0,
            {str(row["term"]): int(row["df"]) for row in rows},
        )
        _SPARSE_STATS_CACHE[cache_key] = stats
        return stats

    def sparse_diagnostic(
        self,
        query_text: str,
        *,
        top_k: int = 3,
        filters: RetrievalFilters | None = None,
        gold_chunk_ids: Sequence[str] = (),
    ) -> dict[str, Any]:
        """Use the search path's query/predicate and return its actual parsed tsqueries."""
        filters = filters or RetrievalFilters()
        with self.database.connect() as conn:
            document_stats = self._document_frequencies(conn)
            document_count, document_frequencies = document_stats
            _, _, dropped_terms = _filtered_sparse_query_texts(
                query_text, document_frequencies, document_count
            )
            terms, source, params = self._sparse_sql(
                query_text, filters, document_stats=document_stats
            )
            query = f"""{terms} SELECT (SELECT count(*) {source}) AS count,
                plain::text AS plain, identifiers::text AS identifiers FROM terms"""
            row = conn.execute(query, params).fetchone()
            top_query = f"""{terms} SELECT c.payload,
                       greatest(ts_rank_cd(c.search_vector, terms.plain),
                                ts_rank_cd(c.identifier_vector, terms.identifiers)) AS score
                {source}
                ORDER BY score DESC, c.id
                LIMIT %s"""
            top_rows = conn.execute(top_query, (*params, top_k)).fetchall()
            rank_rows: list[Any] = []
            if gold_chunk_ids:
                rank_query = f"""{terms}, ranked AS (
                    SELECT c.chunk_key, c.id,
                           greatest(ts_rank_cd(c.search_vector, terms.plain),
                                    ts_rank_cd(c.identifier_vector, terms.identifiers)) AS score
                    {source}
                )
                SELECT chunk_key, score,
                       row_number() OVER (ORDER BY score DESC, id) AS rank
                FROM ranked
                WHERE chunk_key=ANY(%s)"""
                rank_rows = conn.execute(rank_query, (*params, list(gold_chunk_ids))).fetchall()
        matches = tuple(
            ScoredChunk(
                chunk=replace(chunk_from_payload(row["payload"]), access_policy=None),
                sparse_score=float(row["score"]),
                rank=rank,
            )
            for rank, row in enumerate(top_rows, 1)
        )
        ranked_gold = {str(item["chunk_key"]): int(item["rank"]) for item in rank_rows}
        return {
            "plain_tsquery": row["plain"] if row else "",
            "identifier_tsquery": row["identifiers"] if row else "",
            "matching_chunk_count": int(row["count"]) if row else 0,
            "document_count": document_count,
            "dropped_terms": list(dropped_terms),
            "top_chunk_ids": [match.chunk.chunk_id for match in matches],
            "top_matches": [
                {"chunk_id": match.chunk.chunk_id, "score": match.sparse_score, "rank": match.rank}
                for match in matches
            ],
            "gold_chunk_ranks": {
                chunk_id: ranked_gold.get(chunk_id) for chunk_id in gold_chunk_ids
            },
        }

    def expand_parents(
        self, matches: Sequence[ScoredChunk], *, filters: RetrievalFilters
    ) -> tuple[ScoredChunk, ...]:
        parent_keys = tuple(
            dict.fromkeys(match.chunk.parent_id for match in matches if match.chunk.parent_id)
        )
        if not parent_keys:
            return tuple(matches)
        where, params = self._scope_where(filters)
        match_keys = tuple(
            dict.fromkeys([match.chunk.chunk_id for match in matches] + list(parent_keys))
        )
        query = f"""SELECT c.payload FROM chunks c
            JOIN document_versions v ON v.id=c.document_version_id
            WHERE v.status='active' AND c.chunk_key=ANY(%s) AND {where}"""
        with self.database.connect() as conn:
            rows = conn.execute(query, (list(match_keys), *params)).fetchall()
        parents = {
            chunk_from_payload(row["payload"]).chunk_id: chunk_from_payload(row["payload"])
            for row in rows
        }
        allowed_matches = set(parents)
        expanded: list[ScoredChunk] = []
        seen: set[str] = set()
        for match in matches:
            if match.chunk.chunk_id not in allowed_matches:
                continue
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

    def external_public_chunks(
        self,
        matches: Sequence[ScoredChunk],
        filters: RetrievalFilters,
    ) -> tuple[ScoredChunk, ...]:
        """Recheck current ACL/source text immediately before the public-only provider boundary."""
        if not matches:
            return ()
        where, params = self._scope_where(filters)
        with self.database.connect() as conn:
            rows = conn.execute(
                f"""SELECT c.payload FROM chunks c
                JOIN document_versions v ON v.id=c.document_version_id
                WHERE v.status='active' AND c.chunk_key=ANY(%s) AND {where}
                AND EXISTS (SELECT 1 FROM acl pub
                    WHERE pub.document_version_id=v.id AND pub.is_public)""",
                ([m.chunk.chunk_id for m in matches], *params),
            ).fetchall()
        public = {
            chunk.chunk_id: replace(chunk, access_policy=AccessPolicy(public=True))
            for chunk in (chunk_from_payload(r["payload"]) for r in rows)
        }
        return tuple(
            replace(m, chunk=public[m.chunk.chunk_id])
            for m in matches
            if m.chunk.chunk_id in public
        )

    def save_trace(
        self, trace_id: str, query: str, filters: RetrievalFilters, stages: Sequence[dict[str, Any]]
    ) -> None:
        with self.database.connect() as conn:
            conn.execute(
                """INSERT INTO query_traces
                (id, query, requester, product_version, stages)
                VALUES (%s,%s,%s,%s,%s)
                ON CONFLICT (id) DO UPDATE SET stages=EXCLUDED.stages""",
                (trace_id, query, filters.principal, filters.product_version, Jsonb(list(stages))),
            )

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
        clauses.append(
            "EXISTS (SELECT 1 FROM acl a WHERE a.document_version_id=v.id AND ("
            + " OR ".join(acl)
            + "))"
        )
        return " AND ".join(clauses), params
