#!/usr/bin/env python3
"""Fill missing BGE-small vectors in one isolated full-application database.

This script is intentionally insert-only. It refuses every database name except
the explicitly created evidence_rag_full_app_* target family and never migrates,
updates, deletes, truncates, or writes to the protected source databases.
"""

from __future__ import annotations

import argparse
import json
import math
import time
from typing import Any

import psycopg
from psycopg.conninfo import conninfo_to_dict
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from rag_service.retrieval.encoders import Bm25SparseEncoder
from rag_service.retrieval.local_models import SentenceTransformerEncoder
from rag_service.storage.serialization import validate_vectors

EMBEDDER_ID = "bge-small-en-v1.5"
TARGET_PREFIX = "evidence_rag_full_app_"


def target_name(database_url: str) -> str:
    name = str(conninfo_to_dict(database_url).get("dbname") or "")
    if not name.startswith(TARGET_PREFIX):
        raise RuntimeError(
            f"refusing vector rebuild for database {name!r}; "
            f"target must start with {TARGET_PREFIX!r}"
        )
    return name


def fetch_missing(database_url: str, limit: int) -> list[dict[str, Any]]:
    with psycopg.connect(
        database_url,
        row_factory=dict_row,
        connect_timeout=5,
        options="-c default_transaction_read_only=on -c statement_timeout=120000",
    ) as conn:
        identity = conn.execute(
            "SELECT current_database() AS db, current_setting('transaction_read_only') AS ro"
        ).fetchone()
        assert identity is not None
        if identity["ro"] != "on":
            raise RuntimeError(f"inventory connection was not read-only: {identity}")
        return conn.execute(
            """SELECT DISTINCT ON (c.content_hash) c.content_hash, c.text
            FROM public.chunks c
            JOIN public.document_versions v ON v.id=c.document_version_id
            LEFT JOIN public.embeddings e
              ON e.content_hash=c.content_hash AND e.embedder_id=%s
            WHERE v.status='active' AND e.content_hash IS NULL
            ORDER BY c.content_hash
            LIMIT %s""",
            (EMBEDDER_ID, limit),
        ).fetchall()


def verify_vectors(vectors: tuple[tuple[float, ...], ...]) -> None:
    if not vectors or any(len(vector) != 384 for vector in vectors):
        raise RuntimeError("BGE-small returned a non-384-dimensional vector batch")
    for vector in vectors:
        norm = math.sqrt(sum(value * value for value in vector))
        if not math.isfinite(norm) or not math.isclose(norm, 1.0, abs_tol=1e-4):
            raise RuntimeError(f"BGE-small returned a non-normalized vector: norm={norm}")


def insert_batch(database_url: str, rows: list[dict[str, Any]]) -> dict[str, int | float]:
    texts = [str(row["text"]) for row in rows]
    keys = [str(row["content_hash"]) for row in rows]
    encoder = SentenceTransformerEncoder(
        "bge-small", metadata_prefixed=False, query_instruction=True
    )
    started = time.perf_counter()
    dense = encoder.embed(texts)
    verify_vectors(dense)
    sparse = Bm25SparseEncoder().encode(texts)
    vectors = validate_vectors(dense, sparse, len(rows))
    encoding_seconds = time.perf_counter() - started

    with psycopg.connect(database_url, row_factory=dict_row, connect_timeout=5) as conn:
        identity = conn.execute(
            "SELECT current_database() AS db, current_setting('transaction_read_only') AS ro"
        ).fetchone()
        assert identity is not None
        if identity["ro"] == "on":
            raise RuntimeError("target write connection is unexpectedly read-only")
        inserted_embeddings = 0
        for key, (dense_vector, sparse_vector) in zip(keys, vectors, strict=True):
            insert_result = conn.execute(
                """INSERT INTO public.embeddings
                    (content_hash, embedder_id, embedding, sparse_vector, dimensions)
                VALUES (%s, %s, %s::vector, %s, %s)
                ON CONFLICT (content_hash, embedder_id) DO NOTHING""",
                (
                    key,
                    EMBEDDER_ID,
                    json.dumps(dense_vector),
                    Jsonb(sparse_vector),
                    len(dense_vector),
                ),
            )
            inserted_embeddings += insert_result.rowcount

        link_result = conn.execute(
            """INSERT INTO public.chunk_embeddings
                (document_version_id, chunk_id, content_hash, embedder_id)
            SELECT c.document_version_id, c.id, c.content_hash, %s
            FROM public.chunks c
            JOIN public.document_versions v ON v.id=c.document_version_id
            WHERE v.status='active' AND c.content_hash=ANY(%s)
            ON CONFLICT DO NOTHING""",
            (EMBEDDER_ID, keys),
        )
        inserted_links = link_result.rowcount

    result: dict[str, int | float] = {
        "requested_hashes": len(keys),
        "inserted_embeddings": inserted_embeddings,
        "inserted_links": inserted_links,
        "encoding_seconds": round(encoding_seconds, 3),
    }
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--database-url", required=True)
    parser.add_argument("--limit", type=int, default=1024)
    args = parser.parse_args()
    if args.limit < 1:
        raise ValueError("--limit must be positive")
    name = target_name(args.database_url)
    print(f"target={name} embedder={EMBEDDER_ID} batch_limit={args.limit}")
    rows = fetch_missing(args.database_url, args.limit)
    if not rows:
        print("no_missing_hashes=true")
        return
    result = insert_batch(args.database_url, rows)
    print(json.dumps(result, sort_keys=True))
    remaining = len(fetch_missing(args.database_url, 1_000_000))
    print(f"remaining_unique_hashes_at_most={remaining}")


if __name__ == "__main__":
    main()
