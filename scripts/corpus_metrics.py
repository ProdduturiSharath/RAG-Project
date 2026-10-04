#!/usr/bin/env python3
"""Measure parser/chunker counts before the optional evaluation-database load."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from rag_service.benchmark.corpus import parse_postgresql_source
from rag_service.domain import DocumentSection
from rag_service.ingestion.chunking import DeterministicChunker


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--processed-dir", type=Path, default=Path("data/processed/postgresql"))
    parser.add_argument("--output", type=Path, default=Path("data/eval/corpus_metrics.json"))
    args = parser.parse_args()
    chunker = DeterministicChunker(max_tokens=220, overlap_tokens=35)
    metrics: dict[str, object] = {
        "chunker": {"max_tokens": 220, "overlap_tokens": 35},
        "embedder": "bge-small-en-v1.5 (database ingestion script)",
        "embedding_seconds": None,
        "embedding_status": "requires RAG_EVAL_DATABASE_URL and scripts/ingest_postgres_docs.py",
    }
    for version in ("pg-15", "pg-16", "pg-17"):
        records = parse_postgresql_source(args.processed_dir / version, version)
        sections = [
            DocumentSection(
                text=record.text,
                heading=record.title,
                section_path=record.section_path,
                section_id=record.section_id,
                lineage_key=record.lineage_key,
                kind=record.kind,
            )
            for record in records
        ]
        chunks = chunker.chunk(sections, document_id="postgresql-documentation", version=version)
        metrics[version] = {
            "documents": 1,
            "sections": len(records),
            "chunks": len(chunks),
            "table_chunks": sum(chunk.kind == "table" for chunk in chunks),
            "code_chunks": sum(chunk.kind == "code" for chunk in chunks),
        }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(metrics, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(metrics, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
