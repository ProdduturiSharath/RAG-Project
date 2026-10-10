#!/usr/bin/env python3
"""Turn locally extracted PostgreSQL SGML into the benchmark source artifact."""

from __future__ import annotations

import argparse
from pathlib import Path

from rag_service.benchmark.corpus import parse_postgresql_source, write_source_records


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--processed-dir", type=Path, default=Path("data/processed/postgresql"))
    parser.add_argument("--output", type=Path, default=Path("data/eval/source_sections.jsonl"))
    args = parser.parse_args()
    records = []
    for version in ("pg-15", "pg-16", "pg-17"):
        records.extend(parse_postgresql_source(args.processed_dir / version, version))
    if not records:
        raise RuntimeError("no PostgreSQL source records were produced")
    write_source_records(records, args.output)
    by_version = {
        version: sum(record.version == version for record in records)
        for version in ("pg-15", "pg-16", "pg-17")
    }
    print(f"source records: {len(records)}")
    print(f"records per version: {by_version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
