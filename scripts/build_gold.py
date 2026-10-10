#!/usr/bin/env python3
"""Build final Phase 3 gold from the candidate audit and existing reviews."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

REVIEW_METHODS = {"human", "model_audit", "owner_written"}


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()]


def _quotes(row: dict[str, Any]) -> list[str]:
    return [str(span.get("quote", "")) for span in row.get("evidence_spans", [])]


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def build_gold(
    candidates_path: Path,
    audit_path: Path,
    reviewed_path: Path,
    parser_impact_path: Path,
    output_path: Path,
) -> dict[str, Any]:
    candidates = _read_jsonl(candidates_path)
    audit_rows = _read_jsonl(audit_path)
    reviewed_rows = _read_jsonl(reviewed_path)
    parser_impact = json.loads(parser_impact_path.read_text(encoding="utf-8"))

    candidate_by_id = {str(row["id"]): row for row in candidates}
    audit_by_id = {str(row["id"]): row for row in audit_rows}
    reviewed_by_id = {str(row["id"]): row for row in reviewed_rows}
    if len(candidate_by_id) != len(candidates):
        raise ValueError("candidate IDs are not unique")
    if set(audit_by_id) != set(candidate_by_id):
        raise ValueError("model audit IDs must exactly cover candidates")
    if len(reviewed_by_id) != len(reviewed_rows):
        raise ValueError("reviewed IDs are not unique")
    if not set(reviewed_by_id) <= set(candidate_by_id):
        raise ValueError("reviewed row is not present in candidates")

    changed_quote_ids = {
        str(identifier) for identifier in parser_impact.get("changed_quote_ids", [])
    }
    gold: list[dict[str, Any]] = []
    human_ids: set[str] = set()
    repaired_ids: set[str] = set()
    excluded_ids: set[str] = set()

    for candidate in candidates:
        identifier = str(candidate["id"])
        if audit_by_id[identifier].get("decision") != "accept":
            excluded_ids.add(identifier)
            continue

        reviewed = reviewed_by_id.get(identifier)
        repaired_review = False
        if reviewed is not None:
            repaired_review = (
                identifier in changed_quote_ids
                or _quotes(reviewed) != _quotes(candidate)
            )
        if reviewed is not None and not repaired_review:
            if reviewed.get("review_status") != "accepted" or reviewed.get("validated") is not True:
                excluded_ids.add(identifier)
                continue
            row = dict(reviewed)
            row["review_method"] = "human"
            human_ids.add(identifier)
        else:
            row = dict(candidate)
            row["review_status"] = "accepted"
            row["validated"] = True
            row["review_method"] = "model_audit"
            if repaired_review:
                repaired_ids.add(identifier)
        if row.get("review_method") not in REVIEW_METHODS:
            raise ValueError(f"invalid review method for {identifier}")
        if row.get("review_status") != "accepted" or row.get("validated") is not True:
            raise ValueError(f"gold row is not explicitly accepted and validated: {identifier}")
        gold.append(row)

    _write_jsonl(output_path, gold)
    return {
        "candidates": len(candidates),
        "audit_accepted": sum(row.get("decision") == "accept" for row in audit_rows),
        "audit_rejected_or_flagged": sum(row.get("decision") != "accept" for row in audit_rows),
        "gold": len(gold),
        "human": len(human_ids),
        "model_audit": sum(row.get("review_method") == "model_audit" for row in gold),
        "owner_written": sum(row.get("review_method") == "owner_written" for row in gold),
        "repaired_review_fallback": sorted(repaired_ids),
        "excluded": sorted(excluded_ids),
        "output": str(output_path),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidates", type=Path,
                        default=Path("data/eval/candidates.jsonl"))
    parser.add_argument("--audit", type=Path,
                        default=Path("data/eval/model_audit.jsonl"))
    parser.add_argument("--reviewed", type=Path,
                        default=Path("data/eval/reviewed.jsonl"))
    parser.add_argument("--parser-impact", type=Path,
                        default=Path("data/eval/parser-repair-impact.json"))
    parser.add_argument("--output", type=Path, default=Path("data/eval/gold.jsonl"))
    args = parser.parse_args()
    print(json.dumps(build_gold(args.candidates, args.audit, args.reviewed,
                                args.parser_impact, args.output),
                     ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
