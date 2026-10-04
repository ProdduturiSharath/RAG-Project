#!/usr/bin/env python3
"""Build splits, diffs, and the deterministic generated candidate pool."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import yaml

from rag_service.benchmark.corpus import load_source_records, write_source_records
from rag_service.benchmark.dataset import (
    build_split_assignments,
    generate_candidates,
    write_jsonl,
)
from rag_service.benchmark.diffs import build_diffs


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=Path("data/eval/source_sections.jsonl"))
    parser.add_argument("--output-dir", type=Path, default=Path("data/eval"))
    parser.add_argument("--acl-config", type=Path, default=Path("data/acl_demo.yaml"))
    args = parser.parse_args()
    records = load_source_records(args.source)
    assignments = build_split_assignments(records)
    diffs, diff_stats = build_diffs(records)
    acl_config = yaml.safe_load(args.acl_config.read_text(encoding="utf-8"))
    candidates = generate_candidates(records, diffs, assignments, acl_config)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    needed = {
        (str(span["lineage_key"]), str(span["version"]))
        for row in candidates
        for span in row["evidence_spans"]
    }
    blind_seen: set[str] = set()
    compact_records = []
    for record in records:
        key = (record.lineage_key, record.version)
        if key in needed:
            compact_records.append(record)
        elif (
            assignments.get(record.lineage_key) == "blind"
            and record.lineage_key not in blind_seen
        ):
            compact_records.append(record)
            blind_seen.add(record.lineage_key)
    # Keep only evidence and one owner-visible section per blind lineage in the
    # committed artifact; the ignored extracted source is the full corpus.
    write_source_records(compact_records, args.source)
    (args.output_dir / "splits.json").write_text(
        json.dumps(
            {
                "assignments": assignments,
                "splits": {
                    split: sorted(
                        lineage for lineage, value in assignments.items() if value == split
                    )
                    for split in ("train", "dev", "test", "blind")
                },
                "counts": dict(Counter(assignments.values())),
                "blind_pool": sorted(
                    lineage for lineage, split in assignments.items() if split == "blind"
                ),
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    write_jsonl(diffs, args.output_dir / "diffs.jsonl")
    write_jsonl(candidates, args.output_dir / "candidates.jsonl")
    stats = {
        "source_records_per_version": dict(Counter(record.version for record in records)),
        "validation_source_records": len(compact_records),
        "split_counts": dict(Counter(assignments.values())),
        "candidate_counts_dev_test": dict(
            Counter(row["type"] for row in candidates if row["split"] in {"dev", "test"})
        ),
        "candidate_total": len(candidates),
        "diffs": diff_stats,
    }
    (args.output_dir / "benchmark_stats.json").write_text(
        json.dumps(stats, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(stats, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
