#!/usr/bin/env python3
"""Import a manually written JSON batch against the entire local corpus."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml

from rag_service.benchmark.corpus import load_source_records, write_source_records
from rag_service.benchmark.dataset import write_jsonl
from rag_service.benchmark.drafts import DraftImporter


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("batch", type=Path)
    parser.add_argument("--source", type=Path,
                        default=Path("data/processed/source_sections.full.jsonl"))
    parser.add_argument("--eval-dir", type=Path, default=Path("data/eval"))
    args = parser.parse_args()
    root = args.eval_dir
    records = load_source_records(args.source)
    if {r.version for r in records} != {"pg-15", "pg-16", "pg-17"}:
        raise RuntimeError("Full three-version corpus is required")
    assignments = json.loads((root / "splits.json").read_text())["assignments"]
    diffs = [json.loads(line) for line in (root / "diffs.jsonl").read_text().splitlines()]
    importer = DraftImporter(records, assignments, diffs,
                             yaml.safe_load(Path("data/acl_demo.yaml").read_text()))
    candidate_path = root / "candidates.jsonl"
    existing = ([json.loads(line) for line in candidate_path.read_text().splitlines()]
                if candidate_path.exists() else [])
    drafts = json.loads(args.batch.read_text())
    accepted, report = importer.import_batch(drafts, existing)
    for row in accepted:
        row["draft_batch"] = args.batch.name
    write_jsonl([*existing, *accepted], candidate_path)
    # Preserve blind records byte-for-byte at the record level and replace stale
    # non-blind excerpts with complete corrected evidence records only.
    source_path = root / "source_sections.jsonl"
    blind = [r for r in load_source_records(source_path)
             if assignments.get(r.lineage_key) == "blind"]
    needed = {(s["lineage_key"], s["version"]) for row in [*existing, *accepted]
              for s in row["evidence_spans"]}
    write_source_records([*blind, *(r for r in records
                                   if (r.lineage_key, r.version) in needed)], source_path)
    report["batch"] = args.batch.name
    args.batch.with_suffix(".report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
