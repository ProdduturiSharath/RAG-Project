"""Host-only preflight and isolated corpus/embedding caches; no search implementation."""

from __future__ import annotations

import hashlib
import json
from dataclasses import replace
from pathlib import Path
from typing import Any

import psycopg
import yaml
from jsonschema import Draft202012Validator
from psycopg import sql
from psycopg.conninfo import conninfo_to_dict, make_conninfo
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from rag_service.benchmark.validation import validate_dataset
from rag_service.domain import AccessPolicy, Chunk, DocumentSection
from rag_service.ingestion.chunking import DeterministicChunker
from rag_service.retrieval.local_models import embedding_text
from rag_service.retrieval.memory import InMemoryHybridIndex
from rag_service.retrieval.models import RetrievalFilters
from rag_service.retrieval.postgres import PostgresHybridIndex
from rag_service.retrieval.postgres_bm25 import PostgresBm25Index
from rag_service.retrieval.scope import parsed_version_mentions
from rag_service.storage.serialization import chunk_from_payload, chunk_to_payload

from .experiments import ExperimentConfig
from .metrics import normalize
from .phase4_config import SystemConfig

BASE_EMBEDDER = "bge-small-en-v1.5"


def digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                    separators=(",", ":")).encode()).hexdigest()


def atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False,
                                    allow_nan=False) + "\n", encoding="utf-8")
    temporary.replace(path)


def load_gold(config: ExperimentConfig) -> list[dict[str, Any]]:
    path = Path(config.dataset)
    if path.resolve() != Path("data/eval/gold.jsonl").resolve():
        raise ValueError("Phase 4 accepts only data/eval/gold.jsonl, never blind question files")
    rows = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    if len(rows) != config.parameters["expected_rows"] or len({r["id"] for r in rows}) != len(rows):
        raise ValueError("gold must contain 212 unique rows")
    schema = Draft202012Validator(json.loads(Path("data/eval/schema.json").read_text()))
    for row in rows:
        if row["split"] not in {"dev", "test"}:
            raise ValueError("gold must contain only dev/test rows")
        schema.validate(row)
    result = validate_dataset(path, "data/eval/source_sections.jsonl", "data/eval/splits.json",
                              require_targets=False, require_final_gold=True)
    if not result["valid"]:
        raise ValueError("gold validation failed: " + "; ".join(result["errors"]))
    return rows


def policy_groups(policy: dict[str, Any], requester: str) -> tuple[str, ...]:
    return next((tuple(p["groups"]) for p in policy["principals"] if p["id"] == requester), ())


def is_restricted(chunk: Chunk, policy: dict[str, Any]) -> bool:
    path = " / ".join(chunk.section_path).casefold()
    return any(title.casefold() in path for title in policy["restricted_section_titles"])


def allowed(chunk: Chunk, policy: dict[str, Any], requester: str) -> bool:
    return not is_restricted(chunk, policy) or AccessPolicy(
        groups=tuple(policy["restricted_allowed_groups"])
    ).allows(requester, groups=policy_groups(policy, requester))


def chunk_record(chunk: Chunk) -> dict[str, Any]:
    return {"chunk_id": chunk.chunk_id, "document_id": chunk.document_id,
            "text": chunk.text, "normalized_text": normalize(chunk.text),
            "version": chunk.version, "lineage_key": chunk.lineage_key}


def preflight(config: ExperimentConfig, database_url: str, results: Path) -> dict[str, Any]:
    info = conninfo_to_dict(database_url)
    if (info.get("host") != "127.0.0.1" or info.get("port", "5432") != "5432"
            or info.get("dbname") != "evidence_rag_eval"):
        raise ValueError("use Postgres at 127.0.0.1:5432, database evidence_rag_eval")
    dsn = make_conninfo(database_url, connect_timeout="5", options="-c search_path=public")
    try:
        with psycopg.connect(dsn, row_factory=dict_row) as conn:
            counts = conn.execute("""SELECT v.product_version, count(*) AS n
                FROM public.chunks c JOIN public.document_versions v ON v.id=c.document_version_id
                WHERE v.status='active' GROUP BY v.product_version""").fetchall()
            actual = {r["product_version"]: r["n"] for r in counts}
            if actual != config.parameters["expected_chunks"]:
                raise ValueError(f"unexpected active chunk counts: {actual}; expected "
                                 f"{config.parameters['expected_chunks']}; refresh Phase 3 corpus")
            rows = conn.execute("""SELECT c.payload FROM public.chunks c
                JOIN public.document_versions v ON v.id=c.document_version_id
                WHERE v.status='active' ORDER BY c.chunk_key""").fetchall()
            embedding = conn.execute("""SELECT count(*) AS n,
                md5(string_agg(md5(e.embedding::text), '' ORDER BY c.chunk_key)) AS fingerprint
                FROM public.chunks c JOIN public.document_versions v ON v.id=c.document_version_id
                JOIN public.chunk_embeddings ce ON ce.chunk_id=c.id AND ce.embedder_id=%s
                JOIN public.embeddings e ON e.content_hash=ce.content_hash
                    AND e.embedder_id=ce.embedder_id
                WHERE v.status='active' AND e.dimensions=384""", (BASE_EMBEDDER,)).fetchone()
            if not embedding or embedding["n"] != sum(actual.values()):
                raise ValueError("active corpus lacks complete 384-dimensional "
                                 "BGE-small embeddings")
            private = conn.execute("""SELECT count(*) AS n FROM public.document_versions v
                WHERE v.status='active' AND NOT EXISTS (SELECT 1 FROM public.acl a
                WHERE a.document_version_id=v.id AND a.is_public)""").fetchone()
            if private and private["n"]:
                raise ValueError("Phase 3 manual snapshot must be public before "
                                 "simulated ACL overlay")
    except psycopg.Error as exc:
        raise RuntimeError("Postgres preflight failed at 127.0.0.1:5432/evidence_rag_eval; "
                           "check service, credentials, migrations and Phase 3 ingestion") from exc
    gold = load_gold(config)
    # Run the existing builder into a disposable result, never overwrite frozen gold.
    from scripts.build_gold import build_gold

    rebuilt = results / "cache" / "gold-rebuilt.jsonl"
    build_gold(Path("data/eval/candidates.jsonl"), Path("data/eval/model_audit.jsonl"),
               Path("data/eval/reviewed.jsonl"),
               Path("data/eval/parser-repair-impact.json"), rebuilt)
    if rebuilt.read_bytes() != Path(config.dataset).read_bytes():
        raise ValueError("gold is not byte-reproducible from the committed reviews/audit")
    chunks = tuple(chunk_from_payload(row["payload"]) for row in rows)
    policy = yaml.safe_load(Path("data/acl_demo.yaml").read_text())
    version_labels = tuple(sorted({row["target_version"] for row in gold}))
    parsed_version_rows = sum(
        bool(parsed_version_mentions(row["question"], version_labels)) for row in gold
    )
    sparse_index = PostgresHybridIndex(dsn, embedder_id=BASE_EMBEDDER)
    sparse_diagnostics: list[dict[str, Any]] = []
    for row in gold[:5]:
        diagnostic = sparse_index.sparse_diagnostic(
            row["question"],
            filters=RetrievalFilters(
                principal=row["requester"],
                groups=policy_groups(policy, row["requester"]),
            ),
        )
        item = {"id": row["id"], "question": row["question"], **diagnostic}
        sparse_diagnostics.append(item)
        print(
            f"Sparse diagnostic {row['id']}: plain={diagnostic['plain_tsquery']!r}; "
            f"identifier={diagnostic['identifier_tsquery']!r}; "
            f"matches={diagnostic['matching_chunk_count']}; "
            f"top3={diagnostic['top_chunk_ids']}",
            flush=True,
        )
    for row in gold:
        if row["type"] == "acl":
            allowance = bool(set(policy_groups(policy, row["requester"]))
                             & set(policy["restricted_allowed_groups"]))
            if allowance != row["acl_allowance"]:
                raise ValueError(f"ACL label/policy disagreement: {row['id']}")
            paths = [" / ".join(span["section_path"]).casefold() for span in row["evidence_spans"]]
            if not paths or not all(
                any(t.casefold() in path for t in policy["restricted_section_titles"])
                for path in paths
            ):
                raise ValueError(f"ACL evidence is not restricted: {row['id']}")
    source_files = sorted(Path("src/rag_service").rglob("*.py"))
    source_files += [Path("scripts/build_gold.py"), Path("data/eval/schema.json")]
    provenance = {
        "corpus_sha256": digest([row["payload"] for row in rows]),
        "embeddings_fingerprint": embedding["fingerprint"],
        "gold_sha256": hashlib.sha256(Path(config.dataset).read_bytes()).hexdigest(),
        "policy_sha256": digest(policy),
        "code_sha256": digest({str(p): hashlib.sha256(p.read_bytes()).hexdigest()
                               for p in source_files}),
        "chunk_counts": actual, "gold_rows": len(gold),
        "parsed_version_questions": parsed_version_rows,
        "sparse_diagnostics": sparse_diagnostics,
    }
    atomic_json(results / "phase4_preflight.json", provenance)
    print(f"Preflight OK: Postgres reachable, {len(chunks)} chunks, "
          f"{len(gold)} gold rows validated, "
          f"parsed versions={parsed_version_rows}/{len(gold)}",
          flush=True)
    return {"dsn": dsn, "gold": gold, "chunks": chunks, "policy": policy,
            "provenance": provenance}


def rechunk(chunks: tuple[Chunk, ...], tokens: int) -> tuple[Chunk, ...]:
    if tokens == 220:
        return chunks
    groups: dict[tuple[str, str], dict[str, DocumentSection]] = {}
    for chunk in sorted(chunks, key=lambda c: (c.document_id, c.version, c.ordinal)):
        sections = groups.setdefault((chunk.document_id, chunk.version), {})
        key = chunk.section_id or chunk.chunk_id
        if key not in sections:
            if not chunk.parent_text:
                raise ValueError("chunk-size arm needs complete saved section text")
            sections[key] = DocumentSection(
                text=chunk.parent_text,
                heading=chunk.section_path[-1] if chunk.section_path else None,
                section_path=chunk.section_path, section_id=key, lineage_key=chunk.lineage_key,
                source=chunk.source, metadata=chunk.metadata, kind=chunk.kind,
            )
    chunker = DeterministicChunker(max_tokens=tokens, overlap_tokens=35)
    return tuple(c for (doc, version), sections in sorted(groups.items())
                 for c in chunker.chunk(sections.values(), document_id=doc, version=version))


class Snapshot:
    """SQL-compatible evaluation tables, with genuine SQL ACL filtering.

    Corpus materialization only: ranking always uses PostgresHybridIndex or the
    existing in-memory BM25 adapter. Public ingestion tables are never mutated.
    """

    def __init__(self, dsn: str, key: str, chunks: tuple[Chunk, ...],
                 policy: dict[str, Any]) -> None:
        self._base_dsn = dsn
        self.schema = "phase4_" + digest({"key": key, "format": 1})[:20]
        self.dsn = ""
        self.acl_dsn = ""
        self._set_schema(self.schema)
        self.chunks = chunks
        self.policy = policy
        self._adopt_compatible_schema()
        self._memory: dict[tuple[bool, bool], InMemoryHybridIndex] = {}
        self._prepare()

    def _set_schema(self, schema: str) -> None:
        self.schema = schema
        self.dsn = make_conninfo(self._base_dsn, options=f"-c search_path={schema},public")
        self.acl_dsn = make_conninfo(
            self._base_dsn, options=f"-c search_path={schema}_acl,public"
        )

    def _chunk_fingerprint(self) -> str:
        values = sorted(
            "\x1f".join((
                chunk.chunk_id,
                chunk.version,
                chunk.content_hash or "",
                str(is_restricted(chunk, self.policy)).lower(),
            ))
            for chunk in self.chunks
        )
        return hashlib.md5("\x1e".join(values).encode(), usedforsecurity=False).hexdigest()

    def _adopt_compatible_schema(self) -> None:
        """Reuse a prior code-hash snapshot when its materialized corpus matches."""

        expected_count = len(self.chunks)
        expected_fingerprint = self._chunk_fingerprint()
        matches: list[tuple[int, str]] = []
        with psycopg.connect(self._base_dsn) as conn:
            candidates = conn.execute("""
                SELECT n.nspname
                FROM pg_namespace n
                WHERE n.nspname ~ '^phase4_[0-9a-f]{20}$'
                  AND to_regclass(n.nspname || '.manifest') IS NOT NULL
                  AND EXISTS (
                      SELECT 1 FROM pg_namespace acl
                      WHERE acl.nspname = n.nspname || '_acl'
                  )
                ORDER BY n.nspname
            """).fetchall()
            for candidate_row in candidates:
                candidate = str(candidate_row[0])
                identity = conn.execute(sql.SQL("""
                    SELECT count(*) AS count,
                           md5(coalesce(string_agg(
                               c.chunk_key || chr(31) || v.product_version || chr(31) ||
                               c.content_hash || chr(31) || c.restricted::text,
                               chr(30) ORDER BY c.chunk_key), '')) AS fingerprint
                    FROM {}.chunks c
                    JOIN {}.document_versions v ON v.id=c.document_version_id
                """).format(sql.Identifier(candidate), sql.Identifier(candidate))).fetchone()
                if (identity is None or int(identity[0]) != expected_count
                        or identity[1] != expected_fingerprint):
                    continue
                embedding_count = conn.execute(sql.SQL(
                    "SELECT count(*) FROM {}.embeddings"
                ).format(sql.Identifier(candidate))).fetchone()
                matches.append((int(embedding_count[0]) if embedding_count else 0, candidate))
        if matches:
            self._set_schema(max(matches, key=lambda item: (item[0], item[1]))[1])

    def _prepare(self) -> None:
        with psycopg.connect(self.dsn) as conn:
            conn.execute("SELECT pg_advisory_xact_lock(hashtext(%s))", (self.schema,))
            exists = conn.execute("SELECT to_regclass(%s)", (f"{self.schema}.manifest",)).fetchone()
            if exists and exists[0]:
                return
            conn.execute(f"CREATE SCHEMA {self.schema}")
            conn.execute("""CREATE TABLE document_versions (
                id bigint PRIMARY KEY, document_id text, product_version text, status text)""")
            conn.execute("""CREATE TABLE chunks (
                id bigint PRIMARY KEY, document_version_id bigint, chunk_key text UNIQUE,
                parent_key text, text text, content_hash text, payload jsonb, restricted boolean,
                search_vector tsvector GENERATED ALWAYS AS (to_tsvector('simple', text)) STORED,
                identifier_vector tsvector GENERATED ALWAYS AS (
                    to_tsvector('simple', regexp_replace(text, '[_./-]', ' ', 'g'))) STORED)""")
            conn.execute("""CREATE TABLE acl (document_version_id bigint, is_public boolean,
                principal text, group_name text)""")
            conn.execute("""CREATE TABLE embeddings (content_hash text, embedder_id text,
                embedding vector NOT NULL, dimensions integer, sparse_vector jsonb DEFAULT '{}',
                PRIMARY KEY(content_hash, embedder_id))""")
            conn.execute("""CREATE TABLE chunk_embeddings (document_version_id bigint,
                chunk_id bigint, content_hash text, embedder_id text,
                PRIMARY KEY(chunk_id, embedder_id))""")
            versions = {pair: i for i, pair in enumerate(sorted({(c.document_id, c.version)
                                                               for c in self.chunks}), 1)}
            with conn.cursor() as cursor:
                cursor.executemany("INSERT INTO document_versions VALUES (%s,%s,%s,'active')",
                                   [(i, doc, version) for (doc, version), i in versions.items()])
                cursor.executemany("INSERT INTO acl VALUES (%s,true,NULL,NULL)",
                                   [(i,) for i in versions.values()])
                cursor.executemany("""INSERT INTO chunks (id, document_version_id, chunk_key,
                    parent_key, text, content_hash, payload, restricted)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""", [
                    (i, versions[c.document_id, c.version], c.chunk_id, c.parent_id, c.text,
                     c.content_hash, Jsonb(chunk_to_payload(c)), is_restricted(c, self.policy))
                    for i, c in enumerate(self.chunks, 1)])
            # Reuse already-ingested vectors by exact chunk identity, not a guessed model ID.
            conn.execute("""INSERT INTO chunk_embeddings
                SELECT s.document_version_id,s.id,ce.content_hash,ce.embedder_id FROM chunks s
                JOIN public.chunks c ON c.chunk_key=s.chunk_key
                JOIN public.document_versions v ON v.id=c.document_version_id AND v.status='active'
                JOIN public.chunk_embeddings ce ON ce.chunk_id=c.id AND ce.embedder_id=%s""",
                         (BASE_EMBEDDER,))
            conn.execute("""INSERT INTO embeddings SELECT e.content_hash,e.embedder_id,e.embedding,
                e.dimensions,e.sparse_vector FROM public.embeddings e WHERE EXISTS (
                SELECT 1 FROM chunk_embeddings ce WHERE ce.content_hash=e.content_hash
                AND ce.embedder_id=e.embedder_id)""")
            conn.execute("CREATE INDEX ON chunks USING gin(search_vector)")
            conn.execute("CREATE INDEX ON chunks USING gin(identifier_vector)")
            conn.execute("CREATE INDEX ON chunk_embeddings(embedder_id,content_hash)")
            self._acl_views(conn)
            conn.execute("CREATE TABLE manifest AS SELECT 1 AS format")
            conn.execute("ANALYZE chunks")
            conn.execute("ANALYZE embeddings")

    def _acl_views(self, conn: Any) -> None:
        schema = self.schema
        conn.execute(f"CREATE SCHEMA {schema}_acl")
        conn.execute(f"""CREATE VIEW {schema}_acl.document_versions AS
            SELECT id*2+flag AS id,
                document_id || CASE WHEN flag=1 THEN '::acl-restricted' ELSE '' END AS document_id,
                product_version,status FROM {schema}.document_versions CROSS JOIN
                (VALUES (0),(1)) AS flags(flag)""")
        conn.execute(f"""CREATE VIEW {schema}_acl.chunks AS SELECT
            id,document_version_id*2+restricted::int AS document_version_id,
            chunk_key,parent_key,text,
            content_hash,search_vector,identifier_vector,
            jsonb_set(payload, '{{document_id}}', to_jsonb((payload->>'document_id') ||
                CASE WHEN restricted THEN '::acl-restricted' ELSE '' END)) AS payload
            FROM {schema}.chunks""")
        for name in ("chunk_embeddings", "embeddings"):
            conn.execute(f"CREATE VIEW {schema}_acl.{name} AS SELECT * FROM {schema}.{name}")
        conn.execute(f"CREATE TABLE {schema}_acl.acl (LIKE {schema}.acl)")
        conn.execute(f"""INSERT INTO {schema}_acl.acl
            SELECT id*2,true,NULL,NULL FROM {schema}.document_versions""")
        for group in self.policy["restricted_allowed_groups"]:
            conn.execute(f"""INSERT INTO {schema}_acl.acl
                SELECT id*2+1,false,NULL,%s FROM {schema}.document_versions""", (group,))

    def ensure_embeddings(self, config: SystemConfig, encoder: Any) -> None:
        embedder_id = config.embedder_id
        with psycopg.connect(self.dsn) as conn:
            count = conn.execute("SELECT count(*) FROM chunk_embeddings WHERE embedder_id=%s",
                                 (embedder_id,)).fetchone()
            if count and count[0] == len(self.chunks):
                return
            keys = {row[0] for row in conn.execute(
                "SELECT content_hash FROM embeddings WHERE embedder_id=%s", (embedder_id,))}
        inputs = {c.chunk_id: embedding_text(c, config.metadata_prefixed) for c in self.chunks}
        hashes = {c.chunk_id: (hashlib.sha256(inputs[c.chunk_id].encode()).hexdigest()
                              if config.metadata_prefixed
                              else c.content_hash or digest(inputs[c.chunk_id]))
                  for c in self.chunks}
        unique = {hashes[c.chunk_id]: inputs[c.chunk_id] for c in self.chunks}
        missing = sorted(unique.keys() - keys)
        print(f"Embedding {embedder_id}: {len(missing)} new inputs", flush=True)
        for start in range(0, len(missing), 64):
            batch = missing[start:start + 64]
            vectors = encoder.embed([unique[key] for key in batch])
            with psycopg.connect(self.dsn) as conn, conn.cursor() as cursor:
                cursor.executemany("""INSERT INTO embeddings
                    (content_hash,embedder_id,embedding,dimensions) VALUES (%s,%s,%s::vector,%s)
                    ON CONFLICT DO NOTHING""", [(key, embedder_id, json.dumps(vector), len(vector))
                    for key, vector in zip(batch, vectors, strict=True)])
        with psycopg.connect(self.dsn) as conn, conn.cursor() as cursor:
            cursor.executemany("""INSERT INTO chunk_embeddings
                SELECT document_version_id,id,%s,%s FROM chunks WHERE chunk_key=%s
                ON CONFLICT(chunk_id,embedder_id)
                DO UPDATE SET content_hash=EXCLUDED.content_hash""",
                [(hashes[c.chunk_id], embedder_id, c.chunk_id) for c in self.chunks])
            conn.execute("ANALYZE embeddings")
            conn.execute("ANALYZE chunk_embeddings")

    def index(self, config: SystemConfig, *, acl: bool = False) -> Any:
        if config.sparse_method != "bm25":
            return PostgresHybridIndex(self.acl_dsn if acl else self.dsn,
                                       embedder_id=config.embedder_id)
        hybrid = config.search_mode != "sparse"
        key = (acl, hybrid)
        if key not in self._memory:
            index = InMemoryHybridIndex()
            chunks = []
            for chunk in self.chunks:
                restricted = acl and is_restricted(chunk, self.policy)
                chunks.append(replace(
                    chunk,
                    access_policy=AccessPolicy(groups=tuple(self.policy["restricted_allowed_groups"]))
                    if restricted else None,
                ))
            index.upsert(chunks)
            self._memory[key] = index
        if hybrid:
            return PostgresBm25Index(self.acl_dsn if acl else self.dsn,
                                     embedder_id=config.embedder_id,
                                     sparse_index=self._memory[key])
        return self._memory[key]
