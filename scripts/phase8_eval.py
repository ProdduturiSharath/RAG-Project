#!/usr/bin/env python3
"""Measure deterministic Phase 8 ingestion and read-only query latency."""

from __future__ import annotations

import json
import os
import statistics
import time
from pathlib import Path
from typing import Any
from uuid import uuid4

import psycopg
from psycopg.conninfo import conninfo_to_dict, make_conninfo
from psycopg.rows import dict_row

from rag_service.domain import AccessPolicy, DocumentIdentity, DocumentSection, SourceLocation
from rag_service.ingestion import ChunkingConfig, DeterministicChunker
from rag_service.retrieval import Bm25SparseEncoder, HashEmbeddingEncoder, RetrievalFilters
from rag_service.retrieval.postgres import PostgresHybridIndex
from rag_service.retrieval.service import HybridRetriever, RetrievalConfig
from rag_service.storage import PostgresDatabase, PostgresVersionedStore

ROOT = Path(__file__).resolve().parents[1]
PROTECTED_DATABASES = {
    "evidence_rag_eval",
    "evidence_rag_recovery_20261028",
}


def _percentile(values: list[float], fraction: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, int(len(ordered) * fraction))]


def _assert_safe_database(database_url: str, *, allow_demo: bool = False) -> str:
    name = str(conninfo_to_dict(database_url).get("dbname") or "")
    if name in PROTECTED_DATABASES or name == "public_pre_recovery_20261029":
        raise RuntimeError(f"Phase 8 eval refuses protected database {name!r}")
    if not allow_demo and not name.startswith("rag_test_phase8_"):
        raise RuntimeError(f"Phase 8 mutation target must be rag_test_phase8_*, not {name!r}")
    return name


def _seed_documents(store: PostgresVersionedStore, *, start: int, count: int) -> None:
    policy = AccessPolicy(public=True)
    for index in range(start, start + count):
        document_id = f"phase8-benchmark-{index:03d}"
        identity = DocumentIdentity(
            document_id,
            source=SourceLocation(uri=f"demo://phase8/{document_id}"),
            title=f"Phase 8 benchmark document {index}",
            access_policy=policy,
        )
        sections = tuple(
            DocumentSection(
                text=(
                    f"Document {index} records the deterministic benchmark value "
                    f"for max_wal_senders and WAL durability. "
                    f"The stable identifier is benchmark_{index}."
                ),
                heading="Benchmark evidence",
                level=1,
            )
            for _ in range(2)
        )
        store.ingest(identity, sections, "pg-17", access_policy=policy)


def _run(database_url: str) -> dict[str, Any]:
    database = PostgresDatabase(database_url, "migrations")
    database.migrate()
    encoder = HashEmbeddingEncoder(dimensions=256)
    sparse = Bm25SparseEncoder()
    store = PostgresVersionedStore(
        database_url,
        DeterministicChunker(config=ChunkingConfig(max_tokens=80, overlap_tokens=8)),
        embedder=encoder,
        sparse_encoder=sparse,
        embedder_id="hash-v1",
        migrations_path="migrations",
    )
    ingestion_times: list[float] = []
    started = time.perf_counter()
    for _ in range(3):
        batch_started = time.perf_counter()
        _seed_documents(store, start=8 * len(ingestion_times), count=8)
        ingestion_times.append((time.perf_counter() - batch_started) * 1000)

    read_only_url = make_conninfo(database_url, options="-c default_transaction_read_only=on")
    index = PostgresHybridIndex(read_only_url, embedder_id="hash-v1", migrations_path="migrations")
    retriever = HybridRetriever(
        index,
        encoder,
        sparse,
        config=RetrievalConfig(rerank_top_n=10, persist_traces=False),
    )
    queries = (
        "What does WAL protect?",
        "What is max_wal_senders?",
        "Which stable identifier is used?",
        "What is the benchmark value?",
    )
    query_times: list[float] = []
    for query in queries:
        query_started = time.perf_counter()
        result = retriever.retrieve_sync(
            query,
            top_k=5,
            candidate_k=10,
            alpha=0.5,
            filters=RetrievalFilters(principal="phase8", product_version="pg-17"),
        )
        if not result:
            raise RuntimeError(f"benchmark query returned no result: {query}")
        query_times.append((time.perf_counter() - query_started) * 1000)

    with psycopg.connect(
        read_only_url,
        row_factory=dict_row,
        connect_timeout=5,
        options="-c default_transaction_read_only=on",
    ) as conn:
        identity = conn.execute(
            "SELECT current_database() AS db, current_setting('transaction_read_only') AS ro"
        ).fetchone()
        if identity is None:
            raise RuntimeError("database identity query returned no row")
        counts: dict[str, int] = {}
        for table in ("documents", "document_versions", "sections", "chunks", "embeddings"):
            row = conn.execute(f"SELECT count(*) AS n FROM public.{table}").fetchone()
            if row is None:
                raise RuntimeError(f"count query returned no row for {table}")
            counts[table] = int(row["n"])
    if identity["ro"] != "on":
        raise RuntimeError(f"latency benchmark was not read-only: {identity}")
    return {
        "database": identity["db"],
        "read_only": True,
        "vector_backend": "deterministic hash-v1, 256 dimensions",
        "api_cost_usd": 0.0,
        "ingestion_documents": 24,
        "ingestion_batches": 3,
        "ingestion_p50_ms": _percentile(ingestion_times, 0.50),
        "ingestion_p95_ms": _percentile(ingestion_times, 0.95),
        "query_count": len(query_times),
        "query_p50_ms": _percentile(query_times, 0.50),
        "query_p95_ms": _percentile(query_times, 0.95),
        "query_mean_ms": statistics.fmean(query_times),
        "elapsed_seconds": time.perf_counter() - started,
        "counts": counts,
    }


def main() -> None:
    admin_url = os.getenv(
        "RAG_PHASE8_ADMIN_DATABASE_URL",
        "postgresql://postgres:postgres@127.0.0.1:5432/postgres",
    )
    admin_name = str(conninfo_to_dict(admin_url).get("dbname") or "")
    if admin_name not in {"postgres", "template1"}:
        raise RuntimeError("RAG_PHASE8_ADMIN_DATABASE_URL must point to postgres or template1")
    name = "rag_test_phase8_" + uuid4().hex
    database_url = make_conninfo(admin_url, dbname=name)
    with psycopg.connect(admin_url, autocommit=True) as admin:
        admin.execute(f'CREATE DATABASE "{name}" TEMPLATE template0')
    print(f"Created isolated Phase 8 benchmark database: {name}")
    try:
        result = _run(database_url)
        result_path = ROOT / "results/phase8_results.json"
        result_path.write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        table = "\n".join(
            (
                "# Phase 8 benchmark",
                "",
                "| Metric | Value |",
                "|---|---:|",
                f"| Mutation database | `{result['database']}` |",
                f"| Read-only query transactions | `{result['read_only']}` |",
                f"| Vector backend | {result['vector_backend']} |",
                f"| Ingestion batches | {result['ingestion_batches']} |",
                f"| Ingestion p50 (ms) | {result['ingestion_p50_ms']:.3f} |",
                f"| Ingestion p95 (ms) | {result['ingestion_p95_ms']:.3f} |",
                f"| Query count | {result['query_count']} |",
                f"| Query p50 (ms) | {result['query_p50_ms']:.3f} |",
                f"| Query p95 (ms) | {result['query_p95_ms']:.3f} |",
                f"| API cost | `${result['api_cost_usd']:.2f}` |",
                "",
                f"Counts: `{result['counts']}`",
                "",
            )
        )
        (ROOT / "results/phase8_table.md").write_text(table, encoding="utf-8")
        findings = "\n".join(
            (
                "# Phase 8 findings",
                "",
                f"- Demo benchmark mutations ran only in `{result['database']}` and were "
                "dropped after the run.",
                "- Latency queries used `default_transaction_read_only=on`.",
                "- The benchmark used deterministic hash vectors and made no external API calls.",
                "- Measured output: `results/phase8_results.json` and "
                "`results/phase8_table.md`.",
                "- The recovered evaluation databases were not used as mutation targets.",
                "",
                f"- Ingestion p50/p95: `{result['ingestion_p50_ms']:.3f}` / "
                f"`{result['ingestion_p95_ms']:.3f}` ms.",
                f"- Query p50/p95: `{result['query_p50_ms']:.3f}` / "
                f"`{result['query_p95_ms']:.3f}` ms.",
                f"- Seed counts: `{result['counts']}`.",
                "",
                "## Safety boundary",
                "",
                "- Protected databases were not mutation targets.",
                "- The recovered corpus remains a partial-vector reconstruction, not an exact "
                "restoration.",
                "- Docker startup and browser UI smoke testing require a Docker-capable host.",
                "- A PostgreSQL 17 logical dump was unavailable because only a PostgreSQL 15 "
                "client "
                "was installed.",
                "",
                "## Things I am unsure about",
                "",
                "- These timings are local single-process measurements, not production capacity "
                "numbers.",
                "- Docker startup could not be verified in this environment because Docker is "
                "unavailable.",
                "",
            )
        )
        (ROOT / "docs/phase8_findings.md").write_text(findings, encoding="utf-8")
        print(json.dumps(result, indent=2, sort_keys=True))
    finally:
        with psycopg.connect(admin_url, autocommit=True) as admin:
            admin.execute(f'DROP DATABASE "{name}" WITH (FORCE)')
        print(f"Dropped isolated Phase 8 benchmark database: {name}")


if __name__ == "__main__":
    main()
