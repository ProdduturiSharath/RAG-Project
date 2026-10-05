"""Strict, offline validation for the Phase 3 JSONL dataset."""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from .corpus import SourceRecord, load_source_records
from .families import family_map, isolation_errors, manifest_errors, question_lineages
from .gold import gold_version_map

TARGET_COUNTS = {
    "factoid": 35,
    "exact_identifier": 35,
    "table": 25,
    "multi_hop": 12,
    "version_specific": 50,
    "unchanged_control": 25,
    "version_unavailable": 10,
    "unanswerable": 18,
    "acl": 8,
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
    "drafted_by",
    "paraphrased",
    "version_independent",
}
_SPACE_RE = re.compile(r"\s+")


def _source_map(records: list[SourceRecord]) -> dict[tuple[str, str], str]:
    values: dict[tuple[str, str], list[str]] = defaultdict(list)
    for record in records:
        values[(record.lineage_key, record.version)].append(record.text)
        if record.metadata.get("section_lineage"):
            values[(str(record.metadata["section_lineage"]), record.version)].append(record.text)
    return {key: "\n".join(texts) for key, texts in values.items()}


def is_final_gold(row: dict[str, Any]) -> bool:
    """Legacy validated rejected rows are never eligible for final gold."""
    return row.get("validated") is True and row.get("review_status") == "accepted"


def validate_dataset(
    dataset_path: str | Path,
    source_path: str | Path,
    splits_path: str | Path,
    *,
    require_targets: bool = True,
    require_final_gold: bool = False,
    family_manifest_path: str | Path | None = None,
) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
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
            for field in ("answerability", "acl_allowance", "validated", "paraphrased",
                          "version_independent"):
                if not isinstance(row.get(field), bool):
                    errors.append(f"line {number}: {field} must be boolean")
            if row.get("review_status") not in {None, "accepted", "rejected"}:
                errors.append(f"line {number}: unknown review_status")
            if require_final_gold and not is_final_gold(row):
                errors.append(f"line {number}: final gold requires validated accepted review")
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
    gold = gold_version_map(records)
    splits = json.loads(Path(splits_path).read_text(encoding="utf-8"))
    assignments = dict(splits.get("assignments", splits))
    if family_manifest_path is None and splits.get("family_manifest"):
        family_manifest_path = Path(splits_path).parent / splits["family_manifest"]
    mapping = family_map(records)
    if family_manifest_path is not None:
        manifest_path = Path(family_manifest_path)
        if not manifest_path.exists():
            errors.append("complete section-family manifest is missing")
        else:
            manifest = json.loads(manifest_path.read_text())
            errors.extend(manifest_errors(manifest, assignments, records))
            mapping = {key: value["family_key"] for key, value in manifest["lineages"].items()}
    else:
        errors.extend(isolation_errors({k: v for k, v in assignments.items() if k in mapping},
                                       mapping))
    connections = []
    for row in rows:
        if row.get("type") == "multi_hop":
            keys = question_lineages(row)
            if not keys <= mapping.keys():
                errors.append(f"{row.get('id')}: multi-hop lineage lacks family metadata")
            else:
                connections.append({mapping[key] for key in keys})
    errors.extend(isolation_errors({k: v for k, v in assignments.items() if k in mapping},
                                   mapping, connections))
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
        span_gold: list[set[str]] = []
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
            if row.get("version_independent"):
                expected_gold = gold.get((span_lineage, version), [])
                if span.get("gold_versions") != expected_gold:
                    errors.append(f"{row.get('id')}: evidence gold_versions mismatch")
                span_gold.append(set(expected_gold))
        if row.get("version_independent"):
            expected_versions = sorted(set.intersection(*span_gold)) if span_gold else []
            if not expected_versions or row.get("gold_versions") != expected_versions:
                errors.append(f"{row.get('id')}: missing or incorrect gold_versions")
            if not isinstance(spans, list) or not any(
                isinstance(s, dict) and s.get("lineage_key") == lineage for s in spans
            ):
                errors.append(f"{row.get('id')}: primary lineage absent from evidence")
        if split not in {"dev", "test"} and not (
            require_final_gold and split == "blind" and row.get("author") == "human"
        ):
            errors.append(f"{row.get('id', '<unknown>')}: non-dev/test lineage appears in dataset")
        if row.get("author") in {"generated", "llm_drafted"} and row.get("validated"):
            errors.append(f"{row.get('id', '<unknown>')}: draft row cannot be validated")
        if row.get("author") == "llm_drafted" and not row.get("drafted_by"):
            errors.append(f"{row.get('id', '<unknown>')}: drafted_by is required")

    counts = Counter(
        str(row.get("type")) for row in rows if row.get("split") in {"dev", "test"}
    )
    if require_targets:
        for kind, expected in TARGET_COUNTS.items():
            if counts[kind] < expected:
                warnings.append(f"type {kind}: {counts[kind]} rows, drafting target {expected}")
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
        "warnings": warnings,
        "records": len(rows),
        "counts_dev_test": dict(sorted(counts.items())),
        "source_records": len(records),
        "lineages": len(assignments),
        "blind_lineages": len(split_lineages["blind"]),
        "final_gold_records": sum(is_final_gold(row) for row in rows),
    }


__all__ = ["TARGET_COUNTS", "is_final_gold", "validate_dataset"]
