#!/usr/bin/env python3
"""One-time, owner-approved family isolation; fail before writes on count drift."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from rag_service.benchmark.corpus import (
    SourceRecord,
    load_source_records,
    write_source_records,
)
from rag_service.benchmark.dataset import write_jsonl
from rag_service.benchmark.families import (
    connected_families,
    family_map,
    isolation_errors,
    question_lineages,
    resolve_migration,
)

BASELINE = "cee88902701ebe40c1ba028b47a0213ab99ea7c3"
EXPECTED = {"assignment_changes": 4709, "candidate_split_changes": 32,
            "candidate_counts": {"dev": 118, "test": 104}, "candidates": 222,
            "reviews": 6, "blind_lineages": 3497, "mixed_families": 0}


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], text=True)


def jsonl(text: str) -> list[dict[str, Any]]:
    return [json.loads(line) for line in text.splitlines() if line.strip()]


def digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def dump(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    root = Path("data/eval")
    if (root / "split-migration.json").exists():
        raise RuntimeError("Migration already recorded; do not apply it again")
    source = Path("data/processed/source_sections.full.jsonl")
    records = load_source_records(source)
    current = {r.lineage_key for r in records}
    old = json.loads((root / "splits.json").read_text())["assignments"]
    if old != json.loads(git("show", BASELINE + ":data/eval/splits.json"))["assignments"]:
        raise RuntimeError("Assignment baseline changed; stop for owner review")
    candidates_path = root / "candidates.jsonl"
    candidates_bytes = candidates_path.read_bytes()
    if candidates_bytes != git("show", BASELINE + ":data/eval/candidates.jsonl").encode():
        raise RuntimeError("Candidate baseline changed; stop for owner review")
    rows = jsonl(candidates_bytes.decode())
    reviews_path = root / "reviewed.jsonl"
    reviews_bytes = reviews_path.read_bytes()
    reviews = jsonl(reviews_bytes.decode())
    if git("ls-files", "--", str(reviews_path)).strip():
        raise RuntimeError("Reviews must remain untracked")

    # Historical public source metadata resolves retired keys. No private blind
    # question file is opened or searched.
    metadata = list(records)
    for sha in git("log", "--format=%H", BASELINE, "--",
                   "data/eval/source_sections.jsonl").splitlines():
        metadata.extend(SourceRecord.from_json(value) for value in
                        jsonl(git("show", sha + ":data/eval/source_sections.jsonl")))
    mapping = family_map(metadata)
    history = []
    provenance = []
    for sha in git("log", "--format=%H", BASELINE, "--", "data/eval/candidates.jsonl",
                   "data/eval/drafts").splitlines():
        for name in git("ls-tree", "-r", "--name-only", sha, "--",
                        "data/eval/drafts", "data/eval/candidates.jsonl").splitlines():
            if name.endswith(".report.json") or name.endswith("revisions.json"):
                continue
            if name != "data/eval/candidates.jsonl" and not Path(name).name.startswith("batch_"):
                continue
            text = git("show", sha + ":" + name)
            history.extend(jsonl(text) if name.endswith(".jsonl") else json.loads(text))
            provenance.append({"commit": sha, "path": name, "sha256": digest(text.encode())})

    protected: dict[str, set[str]] = defaultdict(set)
    for row in rows + reviews:
        for key in question_lineages(row):
            protected[mapping[key]].add(row["split"])
    exposed = {mapping[key] for row in history + rows + reviews
               for key in question_lineages(row)}
    members = {mapping[key] for key in old}
    connections = [{mapping[key] for key in question_lineages(row)}
                   for row in history + rows + reviews if row.get("type") == "multi_hop"]
    components = [sorted(group) for group in connected_families(members, connections)
                  if len(group) > 1]
    new, decisions = resolve_migration(old, mapping, protected, exposed, connections)
    errors = isolation_errors(new, mapping, components, exposed)
    result = {"assignment_changes": sum(new[k] != v for k, v in old.items()),
              "candidate_split_changes": sum(new[r["lineage_key"]] != r["split"] for r in rows),
              "candidate_counts": dict(Counter(new[r["lineage_key"]] for r in rows)),
              "candidates": len(rows), "reviews": len(reviews),
              "blind_lineages": sum(split == "blind" for split in new.values()),
              "mixed_families": len(errors)}
    print(json.dumps(result, indent=2, sort_keys=True))
    if result != EXPECTED or errors:
        raise RuntimeError("STOP: calculated migration differs from owner-approved proposal")
    candidate_by_id = {r["id"]: r for r in rows}
    if not all(r["id"] in candidate_by_id and r["review_status"] == "accepted"
               and r["validated"] is True and r["split"] == new[r["lineage_key"]]
               and all(value == candidate_by_id[r["id"]].get(key)
                       for key, value in r.items()
                       if key not in {"author", "validated", "review_status"}) for r in reviews):
        raise RuntimeError("Reviews differ from the approved preservation assumptions")
    migrated = [{**row, "split": new[row["lineage_key"]]} for row in rows]
    if not all({k: v for k, v in left.items() if k != "split"} ==
               {k: v for k, v in right.items() if k != "split"}
               for left, right in zip(rows, migrated, strict=True)):
        raise RuntimeError("Candidate content changed")
    if not args.apply:
        return

    entries: dict[str, dict[str, Any]] = {}
    for record in metadata:
        key = record.lineage_key
        if key not in new:
            continue
        entry = entries.setdefault(key, {
            "family_key": mapping[key], "section_id": record.section_id,
            "section_lineage": record.metadata.get("section_lineage"),
            "versions": [], "kinds": [], "active": key in current,
        })
        if record.version not in entry["versions"]:
            entry["versions"].append(record.version)
        if record.kind not in entry["kinds"]:
            entry["kinds"].append(record.kind)
    for entry in entries.values():
        entry["versions"].sort()
        entry["kinds"].sort()
    old_blind = {k for k, split in old.items() if split == "blind"}
    new_blind = {k for k, split in new.items() if split == "blind"}
    old_blind_families = {mapping[k] for k in old_blind}
    new_blind_families = {mapping[k] for k in new_blind}
    migration = {
        "baseline_commit": BASELINE,
        "owner_approval": "Approved in this session, including one-time blind-family correction",
        "exposure_uncertainty": "No additional history known to owner; unsaved/untracked history "
                                "cannot be independently verified",
        "source_sha256": digest(source.read_bytes()), "result": result,
        "original_candidates_sha256": digest(candidates_bytes),
        "reviews_sha256": digest(reviews_bytes), "reviews_preserved": len(reviews),
        "candidate_payload_sha256": digest(json.dumps(
            [{k: v for k, v in r.items() if k != "split"} for r in rows],
            sort_keys=True).encode()),
        "baseline_assignments": old, "approved_assignments": new,
        "changes": [{"lineage_key": k, "family_key": mapping[k], "before": old[k],
                     "after": new[k], "reason": decisions[mapping[k]]}
                    for k in sorted(new) if old[k] != new[k]],
        "blind": {"before_lineages": len(old_blind), "after_lineages": len(new_blind),
                  "removed_lineages": sorted(old_blind - new_blind),
                  "added_lineages": sorted(new_blind - old_blind),
                  "before_families": len(old_blind_families),
                  "after_families": len(new_blind_families),
                  "removed_families": sorted(old_blind_families - new_blind_families)},
        "question_history": provenance,
    }
    manifest = {
        "source_sha256": migration["source_sha256"], "source_records": len(records),
        "active_lineages": len(current), "active_families": len({mapping[k] for k in current}),
        "lineages": entries, "components": components, "exposed_families": sorted(exposed),
    }
    compact = load_source_records(root / "source_sections.jsonl")
    # Keep saved passages for retained blind keys, and add one deterministic
    # full-source record per newly blind key. Evidence sources are unchanged.
    blind_records = {r.lineage_key: r for r in compact if r.lineage_key in new_blind}
    for record in records:
        if record.lineage_key in new_blind:
            blind_records.setdefault(record.lineage_key, record)
    needed = {(s["lineage_key"], version) for row in rows for s in row["evidence_spans"]
              for version in {s["version"], *s.get("gold_versions", [])}}
    evidence_records = [r for r in compact if (r.lineage_key, r.version) in needed]
    dump(root / "section_families.json", manifest)
    dump(root / "split-migration.json", migration)
    dump(root / "splits.json", {
        "assignments": new,
        "splits": {split: sorted(k for k, v in new.items() if v == split)
                   for split in ("train", "dev", "test", "blind")},
        "counts": dict(Counter(new.values())), "blind_pool": sorted(new_blind),
        "blind_families": sorted(new_blind_families),
        "family_manifest": "section_families.json", "migration": "split-migration.json",
    })
    write_jsonl(migrated, candidates_path)
    write_source_records([*blind_records.values(), *evidence_records],
                         root / "source_sections.jsonl")
    if (reviews_path.read_bytes() != reviews_bytes
            or git("ls-files", "--", str(reviews_path)).strip()):
        raise RuntimeError("Review preservation failed")
    print("Preserved all 222 candidate payloads and all six reviews; only 32 row splits changed")


if __name__ == "__main__":
    main()
