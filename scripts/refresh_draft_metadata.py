#!/usr/bin/env python3
"""Backfill gold metadata; optionally apply explicitly handwritten revisions."""

import argparse
import json
from pathlib import Path

import yaml

from rag_service.benchmark.corpus import load_source_records, write_source_records
from rag_service.benchmark.dataset import write_jsonl
from rag_service.benchmark.drafts import DraftImporter


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--revisions", type=Path)
    args = parser.parse_args()
    root = Path("data/eval")
    records = load_source_records("data/processed/source_sections.full.jsonl")
    assignments = json.loads((root / "splits.json").read_text())["assignments"]
    diffs = [json.loads(line) for line in (root / "diffs.jsonl").read_text().splitlines()]
    importer = DraftImporter(records, assignments, diffs,
                             yaml.safe_load(Path("data/acl_demo.yaml").read_text()))
    revisions = json.loads(args.revisions.read_text()) if args.revisions else []
    rows = []
    seen: set[str] = set()
    for line in (root / "candidates.jsonl").read_text().splitlines():
        row = json.loads(line)
        revision = next((r for r in revisions if r["original_question"] == row["question"]), None)
        if revision:
            if revision["action"] == "remove":
                continue
            row.update(revision["replacement"])
            row["revision_reason"] = revision["reason"]
        rows.append(importer.accept(row, seen))
    write_jsonl(rows, root / "candidates.jsonl")
    compact = load_source_records(root / "source_sections.jsonl")
    blind = [r for r in compact if assignments.get(r.lineage_key) == "blind"]
    needed = {(s["lineage_key"], v) for row in rows for s in row["evidence_spans"]
              for v in {s["version"], *s["gold_versions"]}}
    write_source_records([*blind, *(r for r in records
                                   if (r.lineage_key, r.version) in needed)],
                         root / "source_sections.jsonl")
    print(f"Refreshed {len(rows)} rows; gold versions compared against full source text")


if __name__ == "__main__":
    main()
