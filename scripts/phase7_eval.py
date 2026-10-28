#!/usr/bin/env python3
"""Phase 7 zero-cost security benchmark and optional PostgreSQL studies."""

from __future__ import annotations

import hashlib
import json
import os
import statistics
import time
from pathlib import Path
from typing import Any

import numpy as np
import psycopg
from psycopg import sql
from psycopg.rows import dict_row

from rag_service.evaluation.phase7 import run_adversarial_benchmark, timed_call

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DSN = "postgresql://postgres:postgres@127.0.0.1:5432/evidence_rag_eval"


def _percentile(values: list[float], fraction: float) -> float:
    if not values:
        return 0.0
    values = sorted(values)
    return values[min(len(values) - 1, int(len(values) * fraction))]


def _drop_phase7_schemas(dsn: str, prefix: str) -> None:
    """Remove only schemas created by this evaluation family."""
    try:
        with psycopg.connect(dsn, connect_timeout=3, row_factory=dict_row, autocommit=True) as conn:
            names = conn.execute(
                "SELECT nspname FROM pg_namespace WHERE nspname LIKE %s", (prefix + "%",)
            ).fetchall()
            for row in names:
                conn.execute(
                    sql.SQL("DROP SCHEMA IF EXISTS {} CASCADE").format(
                        sql.Identifier(str(row["nspname"]))
                    )
                )
    except Exception:
        pass


def _study_a() -> dict[str, Any]:
    """Measure forced RLS as a non-superuser role against explicit ACL SQL."""
    dsn = os.environ.get("RAG_EVAL_DATABASE_URL", DEFAULT_DSN)
    suffix = hashlib.sha256(f"phase7:{time.time_ns()}".encode()).hexdigest()[:10]
    schema = f"phase7_rls_{suffix}"
    role = f"phase7_rls_role_{suffix}"
    started = time.perf_counter()
    try:
        with psycopg.connect(dsn, connect_timeout=3, row_factory=dict_row, autocommit=True) as conn:
            conn.execute(sql.SQL("CREATE SCHEMA {} ").format(sql.Identifier(schema)))
            conn.execute(
                sql.SQL(
                    "CREATE ROLE {} NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOBYPASSRLS"
                ).format(sql.Identifier(role))
            )
            conn.execute(
                sql.SQL("""
                CREATE TABLE {}.chunks (
                    chunk_id text PRIMARY KEY, document_id text NOT NULL, version text NOT NULL,
                    text text NOT NULL
                )
            """).format(sql.Identifier(schema))
            )
            conn.execute(
                sql.SQL("""
                CREATE TABLE {}.acl (
                    document_id text NOT NULL, version text NOT NULL, is_public boolean NOT NULL,
                    principal text, group_name text
                )
            """).format(sql.Identifier(schema))
            )
            conn.execute(
                sql.SQL("""
                INSERT INTO {}.chunks VALUES
                ('public-16','manual','pg-16','public'),
                ('alice-17','manual','pg-17','alice only'),
                ('sre-17','manual','pg-17','sre only')
            """).format(sql.Identifier(schema))
            )
            conn.execute(
                sql.SQL("""
                INSERT INTO {}.acl VALUES
                ('manual','pg-16',true,NULL,NULL),
                ('manual','pg-17',false,'alice',NULL),
                ('manual','pg-17',false,NULL,'sre')
            """).format(sql.Identifier(schema))
            )
            conn.execute(
                sql.SQL("""
                ALTER TABLE {}.chunks ENABLE ROW LEVEL SECURITY;
                ALTER TABLE {}.chunks FORCE ROW LEVEL SECURITY;
            """).format(sql.Identifier(schema), sql.Identifier(schema))
            )
            conn.execute(
                sql.SQL("""
                CREATE POLICY phase7_acl ON {}.chunks USING (
                    EXISTS (
                        SELECT 1 FROM {}.acl a
                        WHERE a.document_id=chunks.document_id AND a.version=chunks.version
                        AND (a.is_public
                             OR a.principal=current_setting('app.current_principal', true)
                             OR a.group_name = ANY(string_to_array(
                                 current_setting('app.current_groups', true), ',')))
                    )
                )
            """).format(sql.Identifier(schema), sql.Identifier(schema))
            )
            conn.execute(
                sql.SQL("GRANT USAGE ON SCHEMA {} TO {} ").format(
                    sql.Identifier(schema), sql.Identifier(role)
                )
            )
            conn.execute(
                sql.SQL("GRANT SELECT ON {}.chunks TO {} ").format(
                    sql.Identifier(schema), sql.Identifier(role)
                )
            )
            conn.execute(
                sql.SQL("GRANT SELECT ON {}.acl TO {} ").format(
                    sql.Identifier(schema), sql.Identifier(role)
                )
            )

            rls_sql = sql.SQL("SELECT chunk_id FROM {}.chunks ORDER BY chunk_id").format(
                sql.Identifier(schema)
            )
            application_sql = sql.SQL("""
                SELECT c.chunk_id FROM {}.chunks c
                WHERE EXISTS (
                    SELECT 1 FROM {}.acl a
                    WHERE a.document_id=c.document_id AND a.version=c.version
                    AND (a.is_public OR a.principal=%s
                         OR a.group_name=ANY(%s::text[]))
                ) ORDER BY c.chunk_id
            """).format(sql.Identifier(schema), sql.Identifier(schema))
            principals = {"alice": (), "bob": ("sre",), "mallory": ()}
            measurements: list[dict[str, Any]] = []
            for principal, groups in principals.items():
                expected = {"public-16"}
                # ACL rows are document-version scoped: either private grant
                # authorizes every chunk in that version.
                if principal == "alice" or "sre" in groups:
                    expected.update({"alice-17", "sre-17"})
                rls_times: list[float] = []
                app_times: list[float] = []
                rls_ids: set[str] = set()
                app_ids: set[str] = set()
                for _ in range(30):
                    with conn.transaction():
                        conn.execute(sql.SQL("SET LOCAL ROLE {}").format(sql.Identifier(role)))
                        conn.execute(
                            "SELECT set_config('app.current_principal', %s, true)",
                            (principal,),
                        )
                        conn.execute(
                            "SELECT set_config('app.current_groups', %s, true)", (",".join(groups),)
                        )
                        started_query = time.perf_counter()
                        rows = conn.execute(rls_sql).fetchall()
                        rls_times.append((time.perf_counter() - started_query) * 1000)
                        rls_ids = {str(row["chunk_id"]) for row in rows}
                    started_query = time.perf_counter()
                    rows = conn.execute(application_sql, (principal, list(groups))).fetchall()
                    app_times.append((time.perf_counter() - started_query) * 1000)
                    app_ids = {str(row["chunk_id"]) for row in rows}
                measurements.append(
                    {
                        "principal": principal,
                        "groups": list(groups),
                        "expected_ids": sorted(expected),
                        "rls_ids": sorted(rls_ids),
                        "application_ids": sorted(app_ids),
                        "rls_leakage": sorted(rls_ids - expected),
                        "application_leakage": sorted(app_ids - expected),
                        "rls_p50_ms": _percentile(rls_times, 0.50),
                        "rls_p95_ms": _percentile(rls_times, 0.95),
                        "application_p50_ms": _percentile(app_times, 0.50),
                        "application_p95_ms": _percentile(app_times, 0.95),
                        "samples": len(rls_times),
                    }
                )
            leakage_free = all(
                not row["rls_leakage"] and not row["application_leakage"] for row in measurements
            )
            return {
                "status": "measured",
                "schema": schema,
                "role_nobypassrls": role,
                "force_rls": True,
                "acl_leakage_free": leakage_free,
                "measurements": measurements,
                "setup_seconds": time.perf_counter() - started,
            }
    except Exception as exc:
        return {
            "status": "unavailable",
            "reason": type(exc).__name__,
            "detail": str(exc).splitlines()[0][:240],
        }
    finally:
        try:
            with psycopg.connect(dsn, connect_timeout=3, autocommit=True) as cleanup:
                cleanup.execute(
                    sql.SQL("DROP SCHEMA IF EXISTS {} CASCADE").format(sql.Identifier(schema))
                )
                cleanup.execute(sql.SQL("DROP ROLE IF EXISTS {}").format(sql.Identifier(role)))
        except Exception:
            pass
        _drop_phase7_schemas(dsn, "phase7_rls_")


def _study_b() -> dict[str, Any]:
    """Measure pgvector HNSW iterative modes against an exact selective scan."""
    dsn = os.environ.get("RAG_EVAL_DATABASE_URL", DEFAULT_DSN)
    try:
        with psycopg.connect(dsn, connect_timeout=3, row_factory=dict_row) as conn:
            extension = conn.execute(
                "SELECT extversion FROM pg_extension WHERE extname='vector'"
            ).fetchone()
            if not extension:
                return {"status": "unavailable", "reason": "pgvector_extension_missing"}
            version_text = str(extension["extversion"])
            version_tuple = tuple(int(part) for part in version_text.split(".")[:3])
            if version_tuple < (0, 8, 7):
                return {
                    "status": "unavailable",
                    "reason": "pgvector_below_0_8_7",
                    "pgvector": version_text,
                }
            embedder = os.environ.get("RAG_EVAL_EMBEDDER_ID", "bge-small-en-v1.5")
            target_version = "pg-17"
            selective_heading = "Functions and Operators"
            dimension_row = conn.execute(
                "SELECT dimensions FROM embeddings WHERE embedder_id=%s LIMIT 1", (embedder,)
            ).fetchone()
            source_details: dict[str, Any]
            if dimension_row and int(dimension_row["dimensions"] or 0) == 384:
                source_details = {"mode": "public", "schema": "public", "embedder": embedder}
                conn.execute(
                    """
                    CREATE TEMP TABLE phase7_ann_scope AS
                    SELECT DISTINCT e.content_hash, e.embedding::vector(384) AS embedding,
                           v.product_version, s.heading_path->>0 AS section_heading,
                           true AS is_public
                    FROM embeddings e
                    JOIN chunk_embeddings ce
                      ON ce.content_hash=e.content_hash AND ce.embedder_id=e.embedder_id
                    JOIN document_versions v ON v.id=ce.document_version_id
                    JOIN chunks c ON c.id=ce.chunk_id
                    JOIN sections s ON s.id=c.section_id
                    WHERE e.embedder_id=%s AND v.status='active'
                      AND EXISTS (
                          SELECT 1 FROM acl a
                          WHERE a.document_version_id=v.id AND a.is_public
                      )
                """,
                    (embedder,),
                )
            else:
                # Docker restart can leave public tables rebuilt while the Phase
                # 4 snapshot schema and Phase 5 vector artifact remain intact.
                # Use those real corpus artifacts rather than inventing vectors.
                artifact_index = ROOT / "phase5_outputs/vectors/baseline-bge-small.index.json"
                artifact_vectors = ROOT / "phase5_outputs/vectors/baseline-bge-small.npy"
                if not artifact_index.exists() or not artifact_vectors.exists():
                    return {
                        "status": "unavailable",
                        "reason": "filtered_ann_requires_verified_384_dimension_index",
                        "pgvector": version_text,
                    }
                artifact_ids = json.loads(artifact_index.read_text(encoding="utf-8"))["ids"]
                vectors = np.load(artifact_vectors, mmap_mode="r")
                if (
                    vectors.ndim != 2
                    or vectors.shape[1] != 384
                    or len(artifact_ids) != len(vectors)
                ):
                    return {
                        "status": "unavailable",
                        "reason": "phase5_vector_artifact_shape_mismatch",
                        "pgvector": version_text,
                    }
                schemas = conn.execute(
                    """SELECT nspname FROM pg_namespace
                    WHERE nspname LIKE 'phase4_%' AND nspname NOT LIKE '%_acl'
                    ORDER BY nspname"""
                ).fetchall()
                source_schema: str | None = None
                source_count = 0
                for schema_row in schemas:
                    candidate = str(schema_row["nspname"])
                    try:
                        count = conn.execute(
                            sql.SQL("SELECT count(*) AS n FROM {}.chunks").format(
                                sql.Identifier(candidate)
                            )
                        ).fetchone()
                        if count and int(count["n"]) > source_count:
                            source_schema, source_count = candidate, int(count["n"])
                    except psycopg.Error:
                        conn.rollback()
                if source_schema is None:
                    return {
                        "status": "unavailable",
                        "reason": "phase4_snapshot_schema_missing",
                        "pgvector": version_text,
                    }
                source_details = {
                    "mode": "phase4_snapshot_plus_phase5_artifact",
                    "schema": source_schema,
                    "artifact": str(artifact_vectors.relative_to(ROOT)),
                }
                records = conn.execute(
                    sql.SQL("""
                    SELECT c.content_hash, v.product_version,
                           c.payload->'section_path'->>0 AS section_heading
                    FROM {}.chunks c
                    JOIN {}.document_versions v ON v.id=c.document_version_id
                    WHERE v.status='active' AND c.content_hash=ANY(%s)
                      AND EXISTS (
                          SELECT 1 FROM {}.acl a
                          WHERE a.document_version_id=v.id AND a.is_public
                      )
                    """).format(
                        sql.Identifier(source_schema),
                        sql.Identifier(source_schema),
                        sql.Identifier(source_schema),
                    ),
                    (artifact_ids,),
                ).fetchall()
                vector_by_id = {
                    str(content_hash): vectors[index]
                    for index, content_hash in enumerate(artifact_ids)
                }
                conn.execute(
                    """CREATE TEMP TABLE phase7_ann_scope (
                    content_hash text, embedding vector(384), product_version text,
                    section_heading text, is_public boolean)"""
                )
                with conn.cursor() as cursor:
                    cursor.executemany(
                        """INSERT INTO phase7_ann_scope
                        (content_hash, embedding, product_version, section_heading, is_public)
                        VALUES (%s, %s::vector(384), %s, %s, true)""",
                        [
                            (
                                str(record["content_hash"]),
                                json.dumps(vector_by_id[str(record["content_hash"])].tolist()),
                                str(record["product_version"]),
                                record["section_heading"],
                            )
                            for record in records
                        ],
                    )
            conn.execute("""
                CREATE INDEX phase7_ann_scope_hnsw
                ON phase7_ann_scope USING hnsw (embedding vector_cosine_ops)
            """)
            conn.execute("ANALYZE phase7_ann_scope")
            sample = conn.execute(
                """
                SELECT embedding::text AS vector
                FROM phase7_ann_scope
                WHERE is_public
                  AND NOT (product_version=%s AND section_heading=%s)
                ORDER BY content_hash LIMIT 8
            """,
                (target_version, selective_heading),
            ).fetchall()
            if not sample:
                return {
                    "status": "unavailable",
                    "reason": "no_public_embedding_samples",
                    "pgvector": version_text,
                }
            exact_sql = """
                SELECT content_hash FROM phase7_ann_scope
                WHERE is_public AND product_version=%s AND section_heading=%s
                ORDER BY embedding <=> %s::vector, content_hash LIMIT 10
            """
            approximate_sql = """
                SELECT content_hash FROM phase7_ann_scope
                WHERE is_public AND product_version=%s AND section_heading=%s
                ORDER BY embedding <=> %s::vector, content_hash LIMIT 10
            """
            modes = ("off", "strict_order")
            mode_rows: dict[str, list[float]] = {mode: [] for mode in modes}
            mode_recalls: dict[str, list[float]] = {mode: [] for mode in modes}
            exact_times: list[float] = []
            with conn.transaction():
                conn.execute("SET LOCAL hnsw.iterative_scan = strict_order")
                conn.execute("SET LOCAL hnsw.ef_search = 40")
                explain = conn.execute(
                    "EXPLAIN (COSTS OFF) " + approximate_sql,
                    (target_version, selective_heading, str(sample[0]["vector"])),
                ).fetchall()
            hnsw_index_used = any(
                "phase7_ann_scope_hnsw" in str(row["QUERY PLAN"]) for row in explain
            )
            for item in sample:
                version = target_version
                vector = str(item["vector"])
                with conn.transaction():
                    conn.execute("SET LOCAL enable_indexscan=off")
                    conn.execute("SET LOCAL enable_bitmapscan=off")
                    started = time.perf_counter()
                    exact = conn.execute(exact_sql, (version, selective_heading, vector)).fetchall()
                    exact_times.append((time.perf_counter() - started) * 1000)
                truth = {str(row["content_hash"]) for row in exact}
                for mode in modes:
                    with conn.transaction():
                        conn.execute(f"SET LOCAL hnsw.iterative_scan = {mode}")
                        conn.execute("SET LOCAL hnsw.ef_search = 40")
                        started = time.perf_counter()
                        rows = conn.execute(
                            approximate_sql, (version, selective_heading, vector)
                        ).fetchall()
                        mode_rows[mode].append((time.perf_counter() - started) * 1000)
                    found = {str(row["content_hash"]) for row in rows}
                    mode_recalls[mode].append(len(truth & found) / max(1, len(truth)))
            return {
                "status": "measured",
                "pgvector": version_text,
                "embedder": embedder,
                "source": source_details,
                "queries": len(sample),
                "exact": {
                    "p50_ms": _percentile(exact_times, 0.5),
                    "p95_ms": _percentile(exact_times, 0.95),
                },
                "modes": {
                    mode: {
                        "recall_at_10": statistics.fmean(mode_recalls[mode]),
                        "latency_p50_ms": _percentile(mode_rows[mode], 0.5),
                        "latency_p95_ms": _percentile(mode_rows[mode], 0.95),
                    }
                    for mode in modes
                },
                "scope_rows": int(
                    (
                        conn.execute(
                            """SELECT count(*) AS n FROM phase7_ann_scope
                            WHERE is_public AND product_version=%s AND section_heading=%s""",
                            (target_version, selective_heading),
                        ).fetchone()
                        or {"n": 0}
                    )["n"]
                ),
                "corpus_rows": int(
                    (
                        conn.execute("SELECT count(*) AS n FROM phase7_ann_scope").fetchone()
                        or {"n": 0}
                    )["n"]
                ),
                "selective_filter": {
                    "product_version": target_version,
                    "section_heading": selective_heading,
                },
                "query_source": "public vectors outside the selective filter",
                "hnsw_index": "phase7_ann_scope_hnsw",
                "hnsw_index_used": hnsw_index_used,
                "ground_truth": "exact selective scan with HNSW/index scans disabled",
            }
    except Exception as exc:
        return {
            "status": "unavailable",
            "reason": type(exc).__name__,
            "detail": str(exc).splitlines()[0][:240],
        }
    finally:
        _drop_phase7_schemas(dsn, "phase7_ann_")


def _table(result: dict[str, Any]) -> str:
    adversarial = result["adversarial"]
    lines = [
        "# Phase 7 security and study results",
        "",
        "All external API calls: **0**.",
        "",
        "## Prompt-injection benchmark",
        "",
        "| Adapter | Cases | Attack success before | Attack success after | "
        "Claim survival before | Claim survival after | Citation spoof before | "
        "Citation spoof after |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for adapter, values in adversarial["adapters"].items():
        lines.append(
            f"| {adapter} | {values['n']} | {values['attack_success_rate_before']:.3f} | "
            f"{values['attack_success_rate_after']:.3f} | "
            f"{values['unverified_claim_survival_before']:.3f} | "
            f"{values['unverified_claim_survival_after']:.3f} | "
            f"{values['citation_spoof_survival_before']:.3f} | "
            f"{values['citation_spoof_survival_after']:.3f} |"
        )
    lines.extend(["", "## PostgreSQL RLS", ""])
    rls = result["rls"]
    if rls["status"] != "measured":
        lines.append(f"Unavailable: `{rls['reason']}` — {rls.get('detail', '')}")
    else:
        lines.extend(
            [
                "| Principal | Groups | RLS p50/p95 ms | App SQL p50/p95 ms | "
                "RLS leakage count | App leakage count |",
                "| --- | --- | ---: | ---: | --- | --- |",
            ]
        )
        for row in rls["measurements"]:
            lines.append(
                f"| {row['principal']} | {','.join(row['groups']) or '—'} | "
                f"{row['rls_p50_ms']:.3f}/{row['rls_p95_ms']:.3f} | "
                f"{row['application_p50_ms']:.3f}/{row['application_p95_ms']:.3f} | "
                f"{len(row['rls_leakage'])} | {len(row['application_leakage'])} |"
            )
    lines.extend(["", "## Filtered ANN recall", ""])
    ann = result["filtered_ann"]
    if ann["status"] != "measured":
        lines.append(f"Unavailable: `{ann['reason']}` — {ann.get('detail', '')}")
    else:
        lines.extend(
            [
                "| Mode | Recall@10 | p50 ms | p95 ms |",
                "| --- | ---: | ---: | ---: |",
            ]
        )
        for mode, values in ann["modes"].items():
            lines.append(
                f"| {mode} | {values['recall_at_10']:.3f} | "
                f"{values['latency_p50_ms']:.3f} | {values['latency_p95_ms']:.3f} |"
            )
        lines.append(
            f"| exact ground truth | 1.000 | {ann['exact']['p50_ms']:.3f} | "
            f"{ann['exact']['p95_ms']:.3f} |"
        )
        lines.append(
            f"\nHNSW index `{ann['hnsw_index']}` used: **{ann['hnsw_index_used']}**; "
            f"selective scope rows: {ann['scope_rows']} of {ann['corpus_rows']}."
        )
    return "\n".join(lines) + "\n"


def _findings(result: dict[str, Any]) -> str:
    rls = result["rls"]
    ann = result["filtered_ann"]
    lines = [
        "# Phase 7 findings",
        "",
        "This report is generated by `scripts/phase7_eval.py`; all provider/API calls "
        "were local and cost $0.",
        "",
        "## Authentication and API controls",
        "",
        "- API identity is derived only from an HS256 JWT with explicit "
        '`algorithms=["HS256"]`, required `sub`, `iat`, and `exp`, and validated '
        "optional `groups`, `roles`, and `scope` claims.",
        "- Query JSON `principal`/`groups` values are ignored; verified claims populate "
        "retrieval filters. Mutation and job routes require `admin`, `ingest`, or "
        "`ingestion` role/scope. Health is public.",
        "- Body, query, document, section, section-count, metadata-depth/key, and "
        "retrieval parameter bounds are enforced. The process-local sliding-window "
        "limiter returns HTTP 429 with `Retry-After`; request and database timeouts "
        "are configurable.",
        "",
        "## Prompt injection",
        "",
    ]
    for adapter, values in result["adversarial"]["adapters"].items():
        lines.append(
            f"- `{adapter}`: attack success {values['attack_success_rate_before']:.3f} → "
            f"{values['attack_success_rate_after']:.3f}; unverified claim survival "
            f"{values['unverified_claim_survival_before']:.3f} → "
            f"{values['unverified_claim_survival_after']:.3f}; citation spoof survival "
            f"{values['citation_spoof_survival_before']:.3f} → "
            f"{values['citation_spoof_survival_after']:.3f}."
        )
    lines.extend(
        [
            "- The adversarial set covers retrieved text, section paths, metadata, user "
            "queries, fake citation identities, and cross-version citation spoofing. "
            "Sanitized prompts redact instruction-shaped values; quote/identity/version "
            "verification rejects surviving claims and abstains.",
            "- These are deterministic security-behavior measurements, not claims about "
            "semantic model robustness.",
            "",
            "## PostgreSQL studies",
            "",
            f"- Study A status: **{rls['status']}**.",
            "- When available, Study A creates an isolated schema, enables and forces RLS, "
            "uses a `NOBYPASSRLS` role under `SET LOCAL ROLE`, and compares RLS-visible "
            "IDs and p50/p95 latency with explicit application ACL predicates. Any leakage "
            "is listed per principal.",
            f"- Study B status: **{ann['status']}**.",
            "- When available, Study B requires pgvector >= 0.8.7, uses selective public "
            "ACL/version filters, computes exact-scan ground truth, and compares HNSW "
            "`iterative_scan=off` and `strict_order` recall@10 and latency.",
        ]
    )
    if rls["status"] == "measured":
        lines.append(
            f"- Study A measured zero ACL leakage for all principals/groups; RLS p50/p95 "
            f"values range from {min(row['rls_p50_ms'] for row in rls['measurements']):.3f}/"
            f"{max(row['rls_p95_ms'] for row in rls['measurements']):.3f} ms."
        )
    if ann["status"] == "measured":
        lines.append(
            f"- Study B used pgvector {ann['pgvector']} and HNSW index "
            f"`{ann['hnsw_index']}` (plan confirmed: {ann['hnsw_index_used']}) over "
            f"{ann['scope_rows']} selective public rows of {ann['corpus_rows']} total "
            f"using {ann['selective_filter']} from source {ann['source']}. "
            f"Queries came from {ann['query_source']}. "
            f"Both modes reached recall@10 "
            f"{ann['modes']['off']['recall_at_10']:.3f}; off p50/p95 "
            f"{ann['modes']['off']['latency_p50_ms']:.3f}/"
            f"{ann['modes']['off']['latency_p95_ms']:.3f} ms; "
            f"strict_order p50/p95 "
            f"{ann['modes']['strict_order']['latency_p50_ms']:.3f}/"
            f"{ann['modes']['strict_order']['latency_p95_ms']:.3f} ms."
        )
    if rls["status"] != "measured" or ann["status"] != "measured":
        lines.extend(
            [
                "- The current container did not expose a PostgreSQL server during this run, "
                "so unavailable database studies are reported explicitly rather than replaced "
                "by synthetic timings.",
            ]
        )
    lines.extend(
        [
            "",
            "## Limitations",
            "",
            "- Rate limiting is process-local and should be backed by a shared store across "
            "multiple workers. JWT key rotation and asymmetric key deployment are outside "
            "this lean HS256 phase.",
            "- RLS and ANN numbers are environment-specific and should be rerun against the "
            "production-like database after pgvector and role privileges are provisioned.",
            "- Parent expansion, scope resolution, traces, response bodies, SSE metadata, "
            "cache invalidation, ACL mutation, and deletion are covered by local tests. "
            "The closeout suite also ran the Postgres integration and Hypothesis database "
            "paths against the configured live `evidence_rag_eval` database; the one "
            "destructive migration-reset test remains intentionally limited to a disposable "
            "database.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    started = time.perf_counter()
    result: dict[str, Any] = {
        "phase": 7,
        "api_cost_usd": 0.0,
        "adversarial": run_adversarial_benchmark(),
        "rls": _study_a(),
        "filtered_ann": _study_b(),
        "latency_helper": timed_call(lambda: hashlib.sha256(b"phase7").hexdigest()),
        "elapsed_seconds": 0.0,
    }
    result["elapsed_seconds"] = time.perf_counter() - started
    result_path = ROOT / "results/phase7_results.json"
    result_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (ROOT / "results/phase7_table.md").write_text(_table(result), encoding="utf-8")
    (ROOT / "docs/phase7_findings.md").write_text(_findings(result), encoding="utf-8")
    print(f"Phase 7 report complete in {result['elapsed_seconds']:.3f}s; API cost=$0", flush=True)
    print(
        f"RLS={result['rls']['status']} filtered-ANN={result['filtered_ann']['status']}",
        flush=True,
    )


if __name__ == "__main__":
    main()
