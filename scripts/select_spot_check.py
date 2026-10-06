#!/usr/bin/env python3
"""Select a deterministic human spot-check set from the model audit."""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path
from typing import Any


TYPES = (
    "factoid",
    "exact_identifier",
    "table",
    "multi_hop",
    "version_specific",
    "unchanged_control",
    "version_unavailable",
    "unanswerable",
    "acl",
)
REQUIRED_IDS = {
    "draft-257b83c46f868ef6",
    "draft-2698580abdaeb4fb",
}


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidates", type=Path,
                        default=Path("data/eval/candidates.jsonl"))
    parser.add_argument("--audit", type=Path,
                        default=Path("data/eval/model_audit.jsonl"))
    parser.add_argument("--reviewed", type=Path,
                        default=Path("data/eval/reviewed.jsonl"))
    parser.add_argument("--output", type=Path,
                        default=Path("data/eval/spot_check_ids.txt"))
    parser.add_argument("--seed", type=int, default=20261006)
    args = parser.parse_args()

    candidates = _read_jsonl(args.candidates)
    audit_rows = _read_jsonl(args.audit)
    reviewed_rows = _read_jsonl(args.reviewed)
    candidate_by_id = {str(row["id"]): row for row in candidates}
    audit_by_id = {str(row["id"]): row for row in audit_rows}
    if len(candidate_by_id) != len(candidates):
        raise ValueError("candidate IDs are not unique")
    if set(audit_by_id) != set(candidate_by_id):
        raise ValueError("audit IDs must exactly cover candidate IDs")
    if any(row.get("decision") not in {"accept", "reject", "flag"}
           for row in audit_rows):
        raise ValueError("audit contains an invalid decision")

    reviewed_ids = {str(row.get("id")) for row in reviewed_rows if row.get("id")}
    rng = random.Random(args.seed)
    selected: set[str] = set()
    sample_counts: dict[str, int] = {}
    for kind in TYPES:
        eligible = [
            row for row in candidates
            if row.get("type") == kind
            and audit_by_id[str(row["id"])].get("decision") == "accept"
            and str(row["id"]) not in reviewed_ids
        ]
        if len(eligible) < 5:
            raise ValueError(f"fewer than five eligible accepted {kind} items")
        chosen = rng.sample(eligible, 5)
        selected.update(str(row["id"]) for row in chosen)
        sample_counts[kind] = len(chosen)

    flagged_ids = {
        str(row["id"]) for row in candidates
        if audit_by_id[str(row["id"])].get("decision") == "flag"
    }
    forced_ids = REQUIRED_IDS | flagged_ids
    unknown_forced = forced_ids - set(candidate_by_id)
    if unknown_forced:
        raise ValueError(f"forced IDs are not candidates: {sorted(unknown_forced)}")
    selected.update(forced_ids)

    # Preserve candidate order in the ID file; random selection affects membership,
    # while stable ordering makes the interactive review reproducible and readable.
    ordered_ids = [str(row["id"]) for row in candidates if str(row["id"]) in selected]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(ordered_ids) + "\n", encoding="utf-8")
    print(json.dumps({
        "seed": args.seed,
        "sample_per_type": sample_counts,
        "reviewed_excluded": len(reviewed_ids),
        "flagged_forced": sorted(flagged_ids),
        "required_forced": sorted(REQUIRED_IDS),
        "selected": len(ordered_ids),
        "output": str(args.output),
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
