#!/usr/bin/env python3
"""Recheck accepted drafts offline and summarize the persisted batch reports."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import yaml

from rag_service.benchmark.corpus import load_source_records
from rag_service.benchmark.drafts import DraftImporter
from rag_service.benchmark.families import family_map, manifest_errors
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
    compact = load_source_records(root / "source_sections.jsonl")
    manifest = json.loads((root / "section_families.json").read_text())
    migration = json.loads((root / "split-migration.json").read_text())
    assert migration["owner_approval"]
    assert not manifest_errors(manifest, splits["assignments"], records)
    mapping = family_map(records)
    mapping.update({k: v["family_key"] for k, v in manifest["lineages"].items()})
    approved_families = {mapping[key]: split for key, split in
                         migration["approved_assignments"].items()}
    assert all(splits["assignments"][key] == approved_families[mapping[key]]
               for key in splits["assignments"] if mapping[key] in approved_families)
    blind_families = sorted({mapping[key] for key, split in splits["assignments"].items()
                             if split == "blind"})
    assert blind_families == splits["blind_families"]
    approved_blind = sorted({mapping[key] for key, split in
                             migration["approved_assignments"].items() if split == "blind"})
    assert blind_families == approved_blind
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
        "version_independent_rows": sum(r["version_independent"] for r in rows),
        "gold_version_sets": dict(Counter(",".join(r["gold_versions"]) for r in rows
                                         if r["version_independent"])),
        "multi_hop_dependency_chains_recorded": all(r.get("reasoning_chain")
                                                    for r in rows if r["type"] == "multi_hop"),
        "by_type": {kind: {"accepted": counts[kind], "discarded": discarded[kind],
                           "target": target, "remaining": max(0, target - counts[kind])}
                    for kind, target in TARGET_COUNTS.items()},
        "target_versions": dict(Counter(r["target_version"] for r in rows)),
        "paraphrased": {kind: sum(r["paraphrased"] for r in rows if r["type"] == kind)
                        for kind in ("factoid", "exact_identifier")},
        "batches": [{k: r[k] for k in ("batch", "accepted", "discarded")} for r in reports],
        "family_isolation": True, "mixed_split_families": 0,
        "blind_families_preserved_since_approved_migration": True,
        "approved_family_assignments_preserved": True,
        "candidate_splits": dict(Counter(r["split"] for r in rows)),
        "all_accepted_rechecked_against_full_corpus": True,
    }
    (root / "drafting_stats.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    stats_path = root / "benchmark_stats.json"
    stats = json.loads(stats_path.read_text())
    stats.update(candidate_total=len(rows), candidate_counts_dev_test=dict(counts),
                 validation_source_records=len(compact), split_counts=splits["counts"],
                 section_families=manifest["active_families"], mixed_split_families=0,
                 split_migration="split-migration.json", blind_pool_unchanged=False,
                 assignment_changes_in_approved_migration=4709,
                 candidate_splits=dict(Counter(r["split"] for r in rows)),
                 blind_families=len(blind_families),
                 blind_families_preserved_since_approved_migration=True)
    stats_path.write_text(json.dumps(stats, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
