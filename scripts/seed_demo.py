#!/usr/bin/env python3
"""Create and seed the isolated Phase 8 demo database without model inference."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

import psycopg
from psycopg.conninfo import conninfo_to_dict, make_conninfo
from psycopg.rows import dict_row

from rag_service.domain import AccessPolicy, DocumentIdentity, DocumentSection, SourceLocation
from rag_service.ingestion import ChunkingConfig, DeterministicChunker
from rag_service.retrieval import Bm25SparseEncoder, HashEmbeddingEncoder
from rag_service.storage import PostgresDatabase, PostgresVersionedStore

DEMO_DATABASE = "evidence_rag_demo"

DEMO_DOCUMENTS: tuple[dict[str, Any], ...] = (
    {
        "id": "demo-postgres-guide",
        "title": "PostgreSQL operations guide",
        "uri": "demo://postgres-guide",
        "policy": AccessPolicy(public=True),
        "versions": (
            (
                "pg-16",
                (
                    (
                        "Replication",
                        "Set max_wal_senders to 10 for this example.",
                        "text",
                    ),
                    (
                        "Durability",
                        "Write-ahead logging (WAL) protects committed changes.",
                        "text",
                    ),
                ),
            ),
            (
                "pg-17",
                (
                    (
                        "Replication",
                        "Set max_wal_senders to 20 for this example.",
                        "text",
                    ),
                    (
                        "Durability",
                        "Write-ahead logging (WAL) protects committed changes.",
                        "text",
                    ),
                    (
                        "Functions",
                        "Use jsonb_path_query for structured JSON inspection.",
                        "code",
                    ),
                ),
            ),
        ),
    },
    {
        "id": "demo-internal-runbook",
        "title": "Internal operations runbook",
        "uri": "demo://internal-runbook",
        "policy": AccessPolicy(groups=("operations",)),
        "versions": (
            (
                "2026-01",
                (
                    (
                        "Deployments",
                        "Operations verifies the migration checksum before rollout.",
                        "text",
                    ),
                    (
                        "Rollback",
                        "The on-call principal may request a rollback after a failed check.",
                        "text",
                    ),
                ),
            ),
        ),
    },
)


def _database_name(database_url: str) -> str:
    return str(conninfo_to_dict(database_url).get("dbname") or "")


def _assert_demo_name(database_url: str) -> None:
    if _database_name(database_url) != DEMO_DATABASE:
        raise RuntimeError(
            f"seed_demo.py only accepts database {DEMO_DATABASE!r}; "
            f"received {_database_name(database_url)!r}"
        )


def _ensure_empty_database(database_url: str, *, create: bool) -> None:
    _assert_demo_name(database_url)
    admin_url = make_conninfo(database_url, dbname="postgres")
    with psycopg.connect(
        admin_url,
        connect_timeout=3,
        options="-c default_transaction_read_only=on",
    ) as admin:
        exists = bool(
            admin.execute(
                "SELECT 1 FROM pg_database WHERE datname=%s", (DEMO_DATABASE,)
            ).fetchone()
        )

    if exists:
        with psycopg.connect(
            database_url,
            connect_timeout=3,
            options="-c default_transaction_read_only=on",
        ) as conn:
            tables = conn.execute(
                """SELECT table_schema, table_name FROM information_schema.tables
                   WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
                   ORDER BY table_schema, table_name"""
            ).fetchall()
            if tables:
                raise RuntimeError(
                    f"refusing to seed non-empty/existing demo schema: {tables}"
                )
    elif not create:
        raise RuntimeError(f"demo database {DEMO_DATABASE!r} does not exist")
    else:
        with psycopg.connect(admin_url, autocommit=True) as admin:
            admin.execute(f'CREATE DATABASE "{DEMO_DATABASE}" TEMPLATE template0')
        print(f"Created isolated demo database: {DEMO_DATABASE}")


def seed(database_url: str) -> dict[str, Any]:
    database = PostgresDatabase(database_url, "migrations")
    database.migrate()
    store = PostgresVersionedStore(
        database_url,
        DeterministicChunker(config=ChunkingConfig(max_tokens=80, overlap_tokens=8)),
        embedder=HashEmbeddingEncoder(dimensions=256),
        sparse_encoder=Bm25SparseEncoder(),
        embedder_id="hash-v1",
        migrations_path="migrations",
    )
    source_by_id = {
        item["id"]: SourceLocation(uri=item["uri"]) for item in DEMO_DOCUMENTS
    }
    for document in DEMO_DOCUMENTS:
        identity = DocumentIdentity(
            document["id"],
            source=source_by_id[document["id"]],
            title=document["title"],
            access_policy=document["policy"],
            metadata={"demo": True},
        )
        for version, raw_sections in document["versions"]:
            sections = tuple(
                DocumentSection(
                    text=text,
                    heading=heading,
                    level=1,
                    kind=kind,
                    source=source_by_id[document["id"]],
                )
                for heading, text, kind in raw_sections
            )
            result = store.ingest(identity, sections, version, access_policy=document["policy"])
            print(
                f"Seeded {document['id']} {version}: chunks={result.chunk_count} "
                f"revision={result.revision} vectors=deterministic-hash"
            )

    with psycopg.connect(database_url, row_factory=dict_row) as conn:
        counts: dict[str, int] = {}
        for table in (
            "documents",
            "document_versions",
            "sections",
            "chunks",
            "acl",
            "embeddings",
            "chunk_embeddings",
        ):
            row = conn.execute(f"SELECT count(*) AS n FROM public.{table}").fetchone()
            if row is None:
                raise RuntimeError(f"count query returned no row for {table}")
            counts[table] = int(row["n"])
    return counts


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--database-url",
        default="postgresql://postgres:postgres@127.0.0.1:5432/evidence_rag_demo",
    )
    parser.add_argument(
        "--create",
        action="store_true",
        help="create evidence_rag_demo when it does not exist",
    )
    args = parser.parse_args()
    _ensure_empty_database(args.database_url, create=args.create)
    print(json.dumps(seed(args.database_url), indent=2, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"seed_demo.py: {type(exc).__name__}: {exc}", file=sys.stderr)
        raise
