#!/usr/bin/env python3
"""Ingest all three official manuals into the separate evaluation database."""

from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path

from psycopg.conninfo import conninfo_to_dict

from rag_service.benchmark.corpus import load_source_records, parse_postgresql_source
from rag_service.domain import DocumentIdentity, DocumentSection, SourceLocation
from rag_service.ingestion.chunking import DeterministicChunker
from rag_service.retrieval.encoders import Bm25SparseEncoder
from rag_service.retrieval.local_models import SentenceTransformerEncoder
from rag_service.storage.postgres import PostgresVersionedStore


class TimingEmbedder:
    """Measure only model encoding calls, excluding database and chunking time."""

    def __init__(self, encoder: SentenceTransformerEncoder) -> None:
        self.encoder = encoder
        self.total_seconds = 0.0

    def embed(self, texts: tuple[str, ...]) -> tuple[tuple[float, ...], ...]:
        start = time.perf_counter()
        values = self.encoder.embed(texts)
        self.total_seconds += time.perf_counter() - start
        return values

    def embed_chunks(self, chunks: tuple[object, ...]) -> tuple[tuple[float, ...], ...]:
        start = time.perf_counter()
        values = self.encoder.embed_chunks(chunks)  # type: ignore[arg-type]
        self.total_seconds += time.perf_counter() - start
        return values


def _require_evaluation_database(url: str) -> None:
    database = str(conninfo_to_dict(url).get("dbname", ""))
    if not database or "test" in database.lower() or not any(
        word in database.lower() for word in ("eval", "dev")
    ):
        raise ValueError(
            "corpus ingestion requires a separate database named with eval or dev, "
            "not the test database"
        )


def _existing_embedding_count(
    store: PostgresVersionedStore, content_hashes: set[str]
) -> int:
    if not content_hashes:
        return 0
    with store.database.connect() as conn:
        row = conn.execute(
            """SELECT count(*) AS count FROM embeddings
               WHERE embedder_id=%s AND content_hash=ANY(%s)""",
            (store.embedder_id, sorted(content_hashes)),
        ).fetchone()
    return int(row["count"]) if row else 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=Path("data/eval/source_sections.jsonl"))
    parser.add_argument(
        "--processed-dir", type=Path, default=Path("data/processed/postgresql")
    )
    parser.add_argument("--database-url", default=os.getenv("RAG_EVAL_DATABASE_URL", ""))
    parser.add_argument("--embedder", default="bge-small")
    parser.add_argument("--output", type=Path, default=Path("data/eval/ingestion_metrics.json"))
    args = parser.parse_args()
    if not args.database_url:
        raise ValueError("set RAG_EVAL_DATABASE_URL or pass --database-url")
    _require_evaluation_database(args.database_url)
    if args.processed_dir.exists():
        records = []
        for version in ("pg-15", "pg-16", "pg-17"):
            records.extend(parse_postgresql_source(args.processed_dir / version, version))
    else:
        records = load_source_records(args.source)
    embedder = TimingEmbedder(SentenceTransformerEncoder(args.embedder, batch_size=64))
    sparse = Bm25SparseEncoder().fit(record.text for record in records)
    store = PostgresVersionedStore(
        args.database_url,
        DeterministicChunker(max_tokens=220, overlap_tokens=35),
        embedder=embedder,
        sparse_encoder=sparse,
        embedder_id="bge-small-en-v1.5",
        migrations_path="migrations",
        batch_size=64,
    )
    store.migrate()
    metrics: dict[str, object] = {
        "embedder": "bge-small-en-v1.5",
        "database": conninfo_to_dict(args.database_url).get("dbname"),
    }
    for version in ("pg-15", "pg-16", "pg-17"):
        version_records = [record for record in records if record.version == version]
        sections = [
            DocumentSection(
                text=record.text,
                heading=record.title,
                section_path=record.section_path,
                # Block records share a document section ID, while their
                # lineage suffix (#codeN/#tableN) distinguishes repeated
                # source blocks with identical text for storage keys.
                section_id=record.lineage_key,
                lineage_key=record.lineage_key,
                kind=record.kind,
                source=SourceLocation(
                    uri=f"https://www.postgresql.org/docs/{version.removeprefix('pg-')}/",
                    metadata={"source_file": record.source_file, "source_line": record.source_line},
                ),
            )
            for record in version_records
        ]
        prepared_chunks = store.chunker.chunk(
            sections, document_id="postgresql-documentation", version=version
        )
        content_hashes = {
            chunk.content_hash for chunk in prepared_chunks if chunk.content_hash
        }
        reused_embeddings = _existing_embedding_count(store, content_hashes)
        result = store.ingest(
            DocumentIdentity(
                "postgresql-documentation",
                source=SourceLocation(uri="https://www.postgresql.org/docs/"),
                title="PostgreSQL Documentation",
            ),
            sections,
            version,
            source=SourceLocation(uri=f"https://www.postgresql.org/docs/{version.removeprefix('pg-')}/"),
        )
        elapsed = embedder.total_seconds - float(metrics.get("_embedding_seconds", 0.0))
        metrics["_embedding_seconds"] = embedder.total_seconds
        metrics[version] = {
            "documents": 1,
            "sections": len(version_records),
            "chunks": result.chunk_count,
            "unique_embeddings": len(content_hashes),
            "embeddings_reused": reused_embeddings,
            "embeddings_computed": len(content_hashes) - reused_embeddings,
            "table_chunks": sum(chunk.kind == "table" for chunk in result.chunks),
            "code_chunks": sum(chunk.kind == "code" for chunk in result.chunks),
            "embedding_seconds": round(elapsed, 3),
        }
    metrics.pop("_embedding_seconds", None)
    metrics["total_embedding_seconds"] = round(embedder.total_seconds, 3)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(metrics, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(metrics, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
