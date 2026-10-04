"""Strict, offline validation for the Phase 3 JSONL dataset."""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from .corpus import SourceRecord, load_source_records

TARGET_COUNTS = {
    "factoid": 30,
    "exact_identifier": 40,
    "table": 20,
    "multi_hop": 10,
    "version_specific": 40,
    "unchanged_control": 20,
    "version_unavailable": 8,
    "unanswerable": 15,
    "acl": 15,
}
REQUIRED_FIELDS = {
    "id",
    "question",
    "type",
    "expected_answer",
    "evidence_spans",
    "target_version",
    "answerability",
    "requester",
    "acl_allowance",
    "lineage_key",
    "split",
    "author",
    "validated",
}
_SPACE_RE = re.compile(r"\s+")


def _source_map(records: list[SourceRecord]) -> dict[tuple[str, str], str]:
    values: dict[tuple[str, str], list[str]] = defaultdict(list)
    for record in records:
        values[(record.lineage_key, record.version)].append(record.text)
        if record.metadata.get("section_lineage"):
            values[(str(record.metadata["section_lineage"]), record.version)].append(record.text)
    return {key: "\n".join(texts) for key, texts in values.items()}


def validate_dataset(
    dataset_path: str | Path,
    source_path: str | Path,
    splits_path: str | Path,
    *,
    require_targets: bool = True,
) -> dict[str, Any]:
    errors: list[str] = []
    rows: list[dict[str, Any]] = []
    seen_questions: set[str] = set()
    with Path(dataset_path).open(encoding="utf-8") as handle:
        for number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                errors.append(f"line {number}: invalid JSON: {exc}")
                continue
            if not isinstance(row, dict):
                errors.append(f"line {number}: record must be an object")
                continue
            missing = REQUIRED_FIELDS - set(row)
            if missing:
                errors.append(f"line {number}: missing fields {sorted(missing)}")
            for field in ("id", "question", "target_version", "requester", "lineage_key", "author"):
                if not isinstance(row.get(field), str) or not row.get(field):
                    errors.append(f"line {number}: {field} must be a non-empty string")
            for field in ("answerability", "acl_allowance", "validated"):
                if not isinstance(row.get(field), bool):
                    errors.append(f"line {number}: {field} must be boolean")
            question = _SPACE_RE.sub(" ", str(row.get("question", "")).strip().lower())
            if not question:
                errors.append(f"line {number}: question is empty")
            elif question in seen_questions:
                errors.append(f"line {number}: duplicate question")
            seen_questions.add(question)
            if not isinstance(row.get("evidence_spans", []), list):
                errors.append(f"line {number}: evidence_spans must be a list")
            if row.get("type") not in TARGET_COUNTS:
                errors.append(f"line {number}: unknown type {row.get('type')!r}")
            if (
                row.get("type") in {"version_unavailable", "unanswerable"}
                and row.get("answerability")
            ):
                errors.append(
                    f"line {number}: unavailable/unanswerable type must be answerability=false"
                )
            rows.append(row)

    records = load_source_records(source_path)
    sources = _source_map(records)
    splits = json.loads(Path(splits_path).read_text(encoding="utf-8"))
    assignments = dict(splits.get("assignments", splits))
    split_lineages: dict[str, set[str]] = defaultdict(set)
    listed_lineages: dict[str, set[str]] = defaultdict(set)
    for split, lineages in splits.get("splits", {}).items():
        for lineage in lineages:
            if str(lineage) in listed_lineages["all"]:
                errors.append(f"lineage appears in multiple persisted split lists: {lineage}")
            listed_lineages["all"].add(str(lineage))
            listed_lineages[str(split)].add(str(lineage))
    for lineage, split in assignments.items():
        split_lineages[str(split)].add(str(lineage))
    for row in rows:
        lineage = str(row.get("lineage_key", ""))
        split = str(row.get("split", ""))
        if assignments.get(lineage) != split:
            errors.append(
                f"{row.get('id', '<unknown>')}: lineage does not have its persisted split"
            )
        spans = row.get("evidence_spans", [])
        for span in spans if isinstance(spans, list) else []:
            if not isinstance(span, dict):
                errors.append(f"{row.get('id', '<unknown>')}: evidence span must be an object")
                continue
            span_lineage = str(span.get("lineage_key", lineage))
            version = str(span.get("version", row.get("target_version", "")))
            quote = str(span.get("quote", ""))
            if not quote or quote not in sources.get((span_lineage, version), ""):
                errors.append(
                    f"{row.get('id', '<unknown>')}: evidence quote absent for "
                    f"{span_lineage}/{version}"
                )
            if assignments.get(span_lineage) != split:
                errors.append(f"{row.get('id', '<unknown>')}: evidence crosses lineage split")
        if split == "blind" or lineage in split_lineages["blind"]:
            errors.append(f"{row.get('id', '<unknown>')}: blind lineage appears in dataset")
        if row.get("author") == "generated" and row.get("validated"):
            errors.append(f"{row.get('id', '<unknown>')}: generated row cannot be validated")

    counts = Counter(
        str(row.get("type")) for row in rows if row.get("split") in {"dev", "test"}
    )
    if require_targets:
        for kind, expected in TARGET_COUNTS.items():
            if counts[kind] < expected:
                errors.append(f"type {kind}: {counts[kind]} rows, expected at least {expected}")
    split_overlap = {
        lineage: sorted(split for split, lineages in split_lineages.items() if lineage in lineages)
        for lineage in assignments
    }
    overlapping = {lineage: values for lineage, values in split_overlap.items() if len(values) > 1}
    if overlapping:
        errors.append(f"lineages appear in multiple splits: {sorted(overlapping)}")
    return {
        "valid": not errors,
        "errors": errors,
        "records": len(rows),
        "counts_dev_test": dict(sorted(counts.items())),
        "source_records": len(records),
        "lineages": len(assignments),
        "blind_lineages": len(split_lineages["blind"]),
    }


__all__ = ["TARGET_COUNTS", "validate_dataset"]
