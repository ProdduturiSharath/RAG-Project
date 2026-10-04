"""Deterministic template-based question generation and lineage splitting."""

from __future__ import annotations

import hashlib
import json
import re
from collections import defaultdict
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from .corpus import SourceRecord
from .validation import TARGET_COUNTS

_IDENTIFIER_RE = re.compile(
    r"\b[A-Za-z][A-Za-z0-9_]*(?:\.[A-Za-z][A-Za-z0-9_]*)*(?:\(\))?\b"
)


def _hash_bucket(value: str) -> int:
    return int(hashlib.sha256(value.encode()).hexdigest()[:8], 16) % 100


def build_split_assignments(records: Iterable[SourceRecord]) -> dict[str, str]:
    """Assign every lineage once; all versions and blocks share its assignment."""

    assignments: dict[str, str] = {}
    for lineage in sorted({record.lineage_key for record in records}):
        bucket = _hash_bucket(lineage)
        assignments[lineage] = (
            "blind" if bucket < 10 else "train" if bucket < 40 else "dev" if bucket < 70 else "test"
        )
    return assignments


def _record_map(records: Iterable[SourceRecord]) -> dict[tuple[str, str], list[SourceRecord]]:
    grouped: dict[tuple[str, str], list[SourceRecord]] = defaultdict(list)
    for record in records:
        grouped[(record.lineage_key, record.version)].append(record)
    return grouped


def _span(record: SourceRecord, quote: str | None = None) -> dict[str, Any]:
    return {
        "lineage_key": record.lineage_key,
        "version": record.version,
        "quote": quote or record.text,
        "source_file": record.source_file,
        "source_line": record.source_line,
        "section_path": list(record.section_path),
    }


def _title(record: SourceRecord) -> str:
    return record.title or "/".join(record.section_path) or record.section_id


def _first_sentence(text: str) -> str:
    text = text.strip()
    match = re.search(r"[.!?](?:\s|$)", text)
    if match and match.start() > 20:
        return text[: match.start() + 1].strip()
    return text[:240]


def _identifiers(text: str) -> list[str]:
    values: list[str] = []
    for match in _IDENTIFIER_RE.finditer(text):
        value = match.group(0)
        lower = value.lower()
        if value.endswith("()") or "_" in value or "." in value or lower.startswith("pg_"):
            if value not in values:
                values.append(value)
    return values


def _new_candidate(
    number: int,
    question: str,
    kind: str,
    expected_answer: str,
    lineage: str,
    split: str,
    target_version: str,
    evidence: list[dict[str, Any]],
    *,
    answerability: bool = True,
    requester: str = "benchmark-user",
    acl_allowance: bool = True,
) -> dict[str, Any]:
    return {
        "id": f"generated-{number:05d}",
        "question": question,
        "type": kind,
        "expected_answer": expected_answer,
        "evidence_spans": evidence,
        "target_version": target_version,
        "answerability": answerability,
        "requester": requester,
        "acl_allowance": acl_allowance,
        "lineage_key": lineage,
        "split": split,
        "author": "generated",
        "validated": False,
    }


def _take_records(
    records: list[SourceRecord],
    assignments: dict[str, str],
    *,
    kind: str,
    count: int,
) -> list[tuple[SourceRecord, str]]:
    eligible = [
        record for record in records
        if assignments.get(record.lineage_key) in {"dev", "test"} and record.text.strip()
    ]
    return [(record, assignments[record.lineage_key]) for record in eligible[:count]]


def generate_candidates(
    records: list[SourceRecord],
    diffs: list[dict[str, Any]],
    assignments: dict[str, str],
    acl_config: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Generate the requested balanced candidate pool without an LLM."""

    grouped = _record_map(records)
    available = [
        record for record in records
        if assignments.get(record.lineage_key) in {"dev", "test"} and record.text.strip()
    ]
    text_records = [record for record in available if record.kind == "text"]
    table_records = [
        record
        for record in available
        if record.kind == "table"
        and record.table_rows
        and any(cell.strip() for row in record.table_rows for cell in row)
    ]
    identifiers: list[tuple[SourceRecord, str]] = []
    seen_identifiers: set[tuple[str, str]] = set()
    for record in text_records:
        for identifier in _identifiers(record.text):
            key = (record.lineage_key, identifier)
            if key not in seen_identifiers:
                seen_identifiers.add(key)
                identifiers.append((record, identifier))

    rows: list[dict[str, Any]] = []
    next_number = 1
    questions: set[str] = set()

    def add(
        question: str,
        kind: str,
        answer: str,
        record: SourceRecord,
        evidence: list[dict[str, Any]],
        *,
        version: str | None = None,
        answerability: bool = True,
        requester: str = "benchmark-user",
        acl_allowance: bool = True,
    ) -> None:
        nonlocal next_number
        normalized = re.sub(r"\s+", " ", question).strip().lower()
        if normalized in questions:
            question = f"{question} [variant {next_number}]"
        questions.add(re.sub(r"\s+", " ", question).strip().lower())
        split = assignments[record.lineage_key]
        rows.append(
            _new_candidate(
                next_number,
                question,
                kind,
                answer,
                record.lineage_key,
                split,
                version or record.version,
                evidence,
                answerability=answerability,
                requester=requester,
                acl_allowance=acl_allowance,
            )
        )
        next_number += 1

    def available_count(kind: str) -> int:
        return TARGET_COUNTS[kind]

    factoid_records = _take_records(
        text_records, assignments, kind="text", count=available_count("factoid")
    )
    for record, _ in factoid_records:
        quote = _first_sentence(record.text)
        add(
            f"What does the PostgreSQL documentation state in the section {_title(record)}?",
            "factoid",
            quote,
            record,
            [_span(record, quote)],
        )

    identifier_templates = (
        "Which exact identifier is named in the section {title}?",
        "What is the exact PostgreSQL identifier documented under {title}?",
        "Give the identifier exactly as written in {title}.",
    )
    for index, (record, identifier) in enumerate(identifiers[:TARGET_COUNTS["exact_identifier"]]):
        template = identifier_templates[index % len(identifier_templates)]
        add(
            template.format(title=_title(record)),
            "exact_identifier",
            identifier,
            record,
            [_span(record, identifier)],
        )

    for record in table_records[:TARGET_COUNTS["table"]]:
        row = record.table_rows[1] if len(record.table_rows) > 1 else record.table_rows[0]
        row_text = " | ".join(row)
        row_key = row[0] if row else "the first row"
        add(
            f"What row is listed for {row_key} in the {_title(record)} table in {record.version}?",
            "table",
            row_text,
            record,
            [_span(record, "| " + " | ".join(row) + " |")],
        )

    for record in text_records[:TARGET_COUNTS["multi_hop"]]:
        identifiers_here = _identifiers(record.text)
        if not identifiers_here:
            identifiers_here = [_first_sentence(record.text)]
        answer = f"{_first_sentence(record.text)} Identifier: {identifiers_here[0]}"
        quote = identifiers_here[0]
        add(
            f"In {_title(record)}, what is stated and which exact identifier is shown?",
            "multi_hop",
            answer,
            record,
            [_span(record, _first_sentence(record.text)), _span(record, quote)],
        )

    version_templates = {
        "changed_default": "In {version}, what default is documented for {name}?",
        "parameter_added": "In {version}, which parameter was added as {name}?",
        "parameter_removed": "In {version}, which parameter is no longer present: {name}?",
        "parameter_renamed": "What is the new parameter name in {version} for {name}?",
        "table_row_added": "Which row was added in {version} for {name}?",
        "table_row_removed": "Which row was removed before {version} for {name}?",
        "text_changed": "What changed in the {name} text in {version}?",
    }
    change_index = 0
    for diff in diffs:
        lineage = str(diff["lineage_key"])
        if assignments.get(lineage) not in {"dev", "test"}:
            continue
        target = str(diff["to_version"])
        for change in diff["changes"]:
            if change_index >= TARGET_COUNTS["version_specific"]:
                break
            change_kind = str(change["kind"])
            evidence_version = target
            if change_kind in {"parameter_removed", "table_row_removed"}:
                evidence_version = str(diff["from_version"])
            evidence = [
                span for span in diff["evidence"] if span["version"] == evidence_version
            ]
            version_records = grouped.get((lineage, evidence_version), [])
            if not evidence or not version_records:
                continue
            record = version_records[0]
            name = str(change.get("name", "the setting"))
            question = version_templates.get(change_kind, version_templates["text_changed"]).format(
                version=target, name=name
            )
            answer = str(change.get("after") or change.get("before") or evidence[0]["quote"])
            add(
                question,
                "version_specific",
                answer,
                record,
                [_span(record, evidence[0]["quote"])],
                version=target,
            )
            change_index += 1
        if change_index >= TARGET_COUNTS["version_specific"]:
            break

    unchanged: list[tuple[SourceRecord, SourceRecord]] = []
    by_lineage: dict[str, dict[str, list[SourceRecord]]] = defaultdict(lambda: defaultdict(list))
    for record in records:
        by_lineage[record.lineage_key][record.version].append(record)
    for lineage, values in sorted(by_lineage.items()):
        if assignments.get(lineage) not in {"dev", "test"}:
            continue
        for left, right in (("pg-15", "pg-16"), ("pg-16", "pg-17")):
            old = "\n".join(item.text for item in values.get(left, []))
            new = "\n".join(item.text for item in values.get(right, []))
            if old and old == new and values.get(left) and values.get(right):
                unchanged.append((values[left][0], values[right][0]))
    for left_record, right_record in unchanged[:TARGET_COUNTS["unchanged_control"]]:
        add(
            f"What unchanged answer appears in both {left_record.version} and "
            f"{right_record.version} for {_title(left_record)}?",
            "unchanged_control",
            _first_sentence(left_record.text),
            left_record,
            [
                _span(left_record, _first_sentence(left_record.text)),
                _span(right_record, _first_sentence(right_record.text)),
            ],
            version=left_record.version,
        )

    fallback = text_records[0] if text_records else available[0]
    for index in range(TARGET_COUNTS["version_unavailable"]):
        record = available[index % len(available)]
        add(
            f"What does PostgreSQL 14 say about {_title(record)}?",
            "version_unavailable",
            "The requested version is not indexed.",
            record,
            [],
            version="pg-14",
            answerability=False,
        )
    for index in range(TARGET_COUNTS["unanswerable"]):
        record = available[(index + 3) % len(available)]
        add(
            f"What undocumented release codename does {_title(record)} use?",
            "unanswerable",
            "Not answerable from the indexed documentation.",
            record,
            [],
            answerability=False,
        )

    restricted_titles = [
        str(value).lower() for value in (acl_config or {}).get("restricted_section_titles", [])
    ]
    restricted = [
        record for record in text_records
        if any(value in _title(record).lower() for value in restricted_titles)
    ] or [fallback]
    for index in range(TARGET_COUNTS["acl"]):
        record = restricted[index % len(restricted)]
        quote = _first_sentence(record.text)
        add(
            f"What does the restricted section {_title(record)} say?",
            "acl",
            quote,
            record,
            [_span(record, quote)],
            requester="guest",
            acl_allowance=False,
        )

    # Keep generated output bounded and deterministic even if a source has more
    # specialized material than the Phase 3 acceptance targets.
    target_total = sum(TARGET_COUNTS.values())
    return rows[:target_total]


def write_jsonl(rows: Iterable[dict[str, Any]], path: str | Path) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


__all__ = ["build_split_assignments", "generate_candidates", "write_jsonl"]
