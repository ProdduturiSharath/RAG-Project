#!/usr/bin/env python3
"""Recheck accepted drafts offline and summarize the persisted batch reports."""

from __future__ import annotations

import json
import subprocess
from collections import Counter
from pathlib import Path

import yaml

from rag_service.benchmark.corpus import load_source_records
from rag_service.benchmark.drafts import DraftImporter
from rag_service.benchmark.validation import TARGET_COUNTS


def main() -> None:
    root = Path("data/eval")
    rows = [json.loads(line) for line in (root / "candidates.jsonl").read_text().splitlines()]
    splits = json.loads((root / "splits.json").read_text())
    records = load_source_records("data/processed/source_sections.full.jsonl")
    diffs = [json.loads(line) for line in (root / "diffs.jsonl").read_text().splitlines()]
    importer = DraftImporter(records, splits["assignments"], diffs,
                             yaml.safe_load(Path("data/acl_demo.yaml").read_text()))
    seen: set[str] = set()
    for row in rows:
        checked = importer.accept(row, seen)
        assert checked["evidence_spans"] == row["evidence_spans"], row["id"]
        assert checked["gold_versions"] == row["gold_versions"], row["id"]
        assert row["author"] == "llm_drafted" and row["validated"] is False
    # The pre-session commit is the immutable reference for the owner's pool.
    baseline = json.loads(subprocess.check_output(
        ["git", "show", "45a586d:data/eval/splits.json"], text=True))
    assert splits["blind_pool"] == baseline["blind_pool"]
    current_keys = {r.lineage_key for r in records}
    assert all(splits["assignments"][key] == split
               for key, split in baseline["assignments"].items() if key in current_keys)
    old_sources = [json.loads(line) for line in subprocess.check_output(
        ["git", "show", "45a586d:data/eval/source_sections.jsonl"], text=True).splitlines()]
    old_blind = [r for r in old_sources if baseline["assignments"][r["lineage_key"]] == "blind"]
    compact = load_source_records(root / "source_sections.jsonl")
    new_blind = [r.to_json() for r in compact if splits["assignments"][r.lineage_key] == "blind"]
    assert new_blind == old_blind
    reports = [json.loads(path.read_text()) for path in sorted(
        (root / "drafts").glob("batch_*.report.json"))]
    discarded: Counter[str] = Counter()
    for report in reports:
        discarded.update(report["discarded_by_type"])
    counts = Counter(r["type"] for r in rows)
    revisions = json.loads((root / "drafts" / "revisions.json").read_text())
    summary = {
        "accepted": len(rows), "discarded": sum(discarded.values()),
        "removed_after_import": dict(Counter(r["type"] for r in revisions
                                             if r["action"] == "remove")),
        "acl_cases": dict(Counter("allowed" if r["acl_allowance"] else "denied"
                                  for r in rows if r["type"] == "acl")),
        "by_type": {kind: {"accepted": counts[kind], "discarded": discarded[kind],
                           "target": target, "remaining": max(0, target - counts[kind])}
                    for kind, target in TARGET_COUNTS.items()},
        "target_versions": dict(Counter(r["target_version"] for r in rows)),
        "paraphrased": {kind: sum(r["paraphrased"] for r in rows if r["type"] == kind)
                        for kind in ("factoid", "exact_identifier")},
        "batches": [{k: r[k] for k in ("batch", "accepted", "discarded")} for r in reports],
        "blind_pool_unchanged": True, "blind_passages_unchanged": True,
        "surviving_assignments_unchanged": True,
        "all_accepted_rechecked_against_full_corpus": True,
    }
    (root / "drafting_stats.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    stats_path = root / "benchmark_stats.json"
    stats = json.loads(stats_path.read_text())
    stats.update(candidate_total=len(rows), candidate_counts_dev_test=dict(counts),
                 validation_source_records=len(compact))
    stats_path.write_text(json.dumps(stats, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
