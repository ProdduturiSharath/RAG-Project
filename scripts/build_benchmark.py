#!/usr/bin/env python3
"""Refresh diffs/splits from local corrected SGML; never generate questions."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from rag_service.benchmark.corpus import (
    load_source_records,
    parse_postgresql_source,
    write_source_records,
)
from rag_service.benchmark.dataset import build_split_assignments, write_jsonl
from rag_service.benchmark.diffs import build_diffs


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--processed-dir", type=Path, default=Path("data/processed/postgresql"))
    parser.add_argument("--full-source", type=Path,
                        default=Path("data/processed/source_sections.full.jsonl"))
    parser.add_argument("--output-dir", type=Path, default=Path("data/eval"))
    parser.add_argument("--diffs-only", action="store_true")
    args = parser.parse_args()
    if args.diffs_only:
        records = load_source_records(args.full_source)
        diffs, diff_stats = build_diffs(records)
        write_jsonl(diffs, args.output_dir / "diffs.jsonl")
        stats_path = args.output_dir / "benchmark_stats.json"
        stats = json.loads(stats_path.read_text())
        stats["diffs"] = diff_stats
        stats_path.write_text(json.dumps(stats, indent=2, sort_keys=True) + "\n")
        print(json.dumps(diff_stats, indent=2, sort_keys=True))
        return 0
    records = []
    for version in ("pg-15", "pg-16", "pg-17"):
        records.extend(parse_postgresql_source(args.processed_dir / version, version))
    if not records:
        raise RuntimeError("No local corpus; do not refresh empty sources")
    split_path = args.output_dir / "splits.json"
    previous = json.loads(split_path.read_text()) if split_path.exists() else {}
    assignments = build_split_assignments(records, previous.get("assignments"))
    blind = sorted(key for key, split in assignments.items() if split == "blind")
    if previous and blind != previous["blind_pool"]:
        raise RuntimeError("Blind pool changed")
    write_source_records(records, args.full_source)
    # Leave committed blind passages intact. Importing drafts adds exact full
    # source records to this compact, CI-readable evidence artifact.
    source_path = args.output_dir / "source_sections.jsonl"
    if not source_path.exists():
        write_source_records([r for r in records if r.lineage_key in blind], source_path)
    splits = {
        "assignments": assignments,
        "splits": {split: sorted(k for k, v in assignments.items() if v == split)
                   for split in ("train", "dev", "test", "blind")},
        "counts": dict(Counter(assignments.values())), "blind_pool": blind,
    }
    split_path.write_text(json.dumps(splits, indent=2, sort_keys=True) + "\n")
    diffs, diff_stats = build_diffs(records)
    write_jsonl(diffs, args.output_dir / "diffs.jsonl")
    current = {r.lineage_key for r in records}
    old = previous.get("assignments", {})
    stats = {
        "source_records_per_version": dict(Counter(r.version for r in records)),
        "split_counts": splits["counts"], "diffs": diff_stats,
        "preserved_surviving_assignments": len(current & old.keys()),
        "new_lineages": len(current - old.keys()),
        "retired_lineages": len(old.keys() - current),
        "retained_retired_blind": len(set(blind) - current),
        "blind_pool_unchanged": blind == previous.get("blind_pool", blind),
        "validation_source_records": len(load_source_records(source_path)),
    }
    (args.output_dir / "benchmark_stats.json").write_text(
        json.dumps(stats, indent=2, sort_keys=True) + "\n")
    print(json.dumps(stats, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
