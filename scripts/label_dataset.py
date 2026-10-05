#!/usr/bin/env python3
"""Small terminal-only review and blind-authoring tool for JSONL labels."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from rag_service.benchmark.corpus import SourceRecord, load_source_records


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def _append(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def _show_evidence(row: dict[str, Any]) -> None:
    fields = ("id", "question", "type", "expected_answer", "target_version", "split")
    print(json.dumps({key: row.get(key) for key in fields}, indent=2))
    print("Evidence:")
    for span in row.get("evidence_spans", []):
        print(f"[{span.get('version')}] {span.get('quote')}")


def review(args: argparse.Namespace) -> int:
    candidates = _read_jsonl(args.candidates)
    output = args.output
    reviewed = {str(row.get("id")): row for row in _read_jsonl(output)}
    for candidate in candidates:
        if str(candidate.get("id")) in reviewed:
            continue
        _show_evidence(candidate)
        action = input("[a]ccept, [e]dit, [r]eject, [q]uit: ").strip().lower()
        if action == "q":
            break
        if action == "r":
            row = dict(candidate)
            row.update({"validated": False, "review_status": "rejected", "author": "human"})
        elif action in {"a", "e"}:
            row = dict(candidate)
            if action == "e":
                question = input(f"Question [{row['question']}]: ").strip()
                answer = input(f"Expected answer [{row['expected_answer']}]: ").strip()
                if question:
                    row["question"] = question
                if answer:
                    row["expected_answer"] = answer
            row.update({"validated": True, "review_status": "accepted", "author": "human"})
        else:
            print("Please choose a, e, r, or q.")
            continue
        _append(output, row)
    return 0


def _blind_records(source: list[SourceRecord], splits: dict[str, Any]) -> list[SourceRecord]:
    assignments = dict(splits.get("assignments", splits))
    return [record for record in source if assignments.get(record.lineage_key) == "blind"]


def write_blind(args: argparse.Namespace) -> int:
    split_values = json.loads(args.splits.read_text(encoding="utf-8"))
    records = _blind_records(load_source_records(args.source), split_values)
    if not records:
        raise RuntimeError("the persisted split file has no blind records")
    print(f"Blind pool contains {len(records)} sections. Enter q at any prompt to stop.")
    for record in records:
        print(f"\n[{record.version}] {' / '.join(record.section_path)}\n{record.text}\n")
        question = input("Question (q to stop): ").strip()
        if question.lower() == "q":
            break
        answer = input("Expected answer (blank if unanswerable): ").strip()
        quote = input("Exact evidence span (blank for unanswerable): ").strip()
        if quote and quote not in record.text:
            print("That span is not present in the displayed section; try this section again.")
            continue
        digest = hashlib.sha256(f"{question}\0{record.lineage_key}".encode()).hexdigest()[:16]
        row = {
            "id": f"blind-{digest}",
            "question": question,
            "type": "factoid",
            "expected_answer": answer,
            "evidence_spans": [] if not quote else [{
                "lineage_key": record.lineage_key,
                "version": record.version,
                "quote": quote,
                "source_file": record.source_file,
                "source_line": record.source_line,
                "section_path": list(record.section_path),
            }],
            "target_version": record.version,
            "answerability": bool(answer),
            "requester": "owner",
            "acl_allowance": True,
            "lineage_key": record.lineage_key,
            "split": "blind",
            "author": "human",
            "validated": True,
            "review_status": "accepted",
            "drafted_by": "owner",
            "paraphrased": False,
            "version_independent": False,
            "gold_versions": [],
        }
        _append(args.output, row)
        print(f"saved {row['id']}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="mode", required=True)
    review_parser = subparsers.add_parser("review")
    review_parser.add_argument(
        "--candidates", type=Path, default=Path("data/eval/candidates.jsonl")
    )
    review_parser.add_argument("--output", type=Path, default=Path("data/eval/reviewed.jsonl"))
    review_parser.set_defaults(function=review)
    write_parser = subparsers.add_parser("write")
    write_parser.add_argument(
        "--source", type=Path, default=Path("data/eval/source_sections.jsonl")
    )
    write_parser.add_argument("--splits", type=Path, default=Path("data/eval/splits.json"))
    write_parser.add_argument("--output", type=Path, default=Path("data/eval/blind.jsonl"))
    write_parser.set_defaults(function=write_blind)
    args = parser.parse_args()
    return int(args.function(args))


if __name__ == "__main__":
    raise SystemExit(main())
