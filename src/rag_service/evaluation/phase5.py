"""Pure data guards and small helpers shared by the Phase 5 stages.

This module deliberately has no torch, Postgres, HTTP, or model imports.  The
host and GPU entry points can therefore validate their inputs independently,
and the important leakage/false-negative rules remain cheap to test.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Iterable, Mapping, Sequence
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

IDENTIFIER_RE = re.compile(r"\b[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)?\b")
STYLE_NAMES = ("identifier", "behavior", "troubleshooting", "keyword")


def normalize(text: str) -> str:
    """Normalize whitespace in the same conservative way as Phase 4."""

    return " ".join(str(text).split())


def text_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
    ]


def family_map(manifest: Mapping[str, Any]) -> dict[str, str]:
    return {
        str(lineage): str(values["family_key"])
        for lineage, values in manifest.get("lineages", {}).items()
        if isinstance(values, Mapping) and values.get("family_key")
    }


def family_split_map(assignments: Mapping[str, str], manifest: Mapping[str, Any]) -> dict[str, str]:
    """Return a family->split map and reject mixed-family assignments."""

    lineage_families = family_map(manifest)
    values: dict[str, set[str]] = {}
    for lineage, split in assignments.items():
        family = lineage_families.get(str(lineage), str(lineage))
        values.setdefault(family, set()).add(str(split))
    mixed = {family: sorted(splits) for family, splits in values.items() if len(splits) != 1}
    if mixed:
        raise ValueError(f"section family has multiple splits: {next(iter(mixed.items()))}")
    return {family: next(iter(splits)) for family, splits in values.items()}


def record_family(record: Mapping[str, Any], manifest: Mapping[str, Any]) -> str:
    lineage = str(record.get("lineage_key", ""))
    lineage_values = manifest.get("lineages", {}).get(lineage, {})
    if isinstance(lineage_values, Mapping) and lineage_values.get("family_key"):
        return str(lineage_values["family_key"])
    parent = str(record.get("metadata", {}).get("section_lineage", ""))
    parent_values = manifest.get("lineages", {}).get(parent, {})
    if isinstance(parent_values, Mapping) and parent_values.get("family_key"):
        return str(parent_values["family_key"])
    return lineage


def record_split(
    record: Mapping[str, Any], assignments: Mapping[str, str], manifest: Mapping[str, Any]
) -> str | None:
    family = record_family(record, manifest)
    splits = family_split_map(assignments, manifest)
    if family in splits:
        return splits[family]
    lineage = str(record.get("lineage_key", ""))
    return assignments.get(lineage)


def assert_train_family(
    record: Mapping[str, Any], assignments: Mapping[str, str], manifest: Mapping[str, Any]
) -> None:
    split = record_split(record, assignments, manifest)
    if split != "train":
        raise ValueError(
            f"record {record.get('lineage_key', '<missing>')} belongs to {split!r}, not train"
        )


def is_reference_only(record: Mapping[str, Any]) -> bool:
    metadata = record.get("metadata", {})
    if isinstance(metadata, Mapping) and bool(metadata.get("reference_only")):
        return True
    lineage = str(record.get("lineage_key", ""))
    if lineage.startswith("pg-section:xref-restored-"):
        return True
    text = normalize(str(record.get("text", ""))).casefold()
    if not text:
        return True
    return bool(re.fullmatch(r"(?:see|refer to|xref|cross-reference)\b.*", text))


def qualifying_passage(record: Mapping[str, Any]) -> bool:
    text = str(record.get("text", ""))
    kind = str(record.get("kind", ""))
    return kind in {"text", "table"} and 200 <= len(text) <= 1800 and not is_reference_only(record)


def gold_quotes(rows: Iterable[Mapping[str, Any]]) -> set[str]:
    return {
        normalize(str(span.get("quote", "")))
        for row in rows
        for span in row.get("evidence_spans", ())
        if normalize(str(span.get("quote", "")))
    }


def passage_exposes_gold_quote(text: str, quotes: Iterable[str]) -> str | None:
    normalized = normalize(text)
    return next((quote for quote in quotes if quote and quote in normalized), None)


def near_duplicate(left: str, right: str, threshold: float = 0.92) -> bool:
    a, b = normalize(left).casefold(), normalize(right).casefold()
    if not a or not b:
        return False
    if a == b:
        return True
    return SequenceMatcher(None, a, b, autojunk=False).ratio() >= threshold


def exclusion_match(text: str, exclusions: Iterable[str], threshold: float = 0.92) -> str | None:
    return next((item for item in exclusions if near_duplicate(text, item, threshold)), None)


def identifiers(text: str) -> set[str]:
    values = set(IDENTIFIER_RE.findall(text))
    calls = set(re.findall(r"\b[A-Za-z_][A-Za-z0-9_]*\s*\(", text))
    return {
        value.casefold()
        for value in values
        if "_" in value or any(char.isdigit() for char in value)
    } | {value.rstrip("(").casefold() for value in calls}


def violates_behavior_style(query: str, passage: str) -> str | None:
    query_ids = identifiers(query)
    return next(
        (identifier for identifier in identifiers(passage) if identifier in query_ids), None
    )


def hard_negative_allowed(positive: Mapping[str, Any], negative: Mapping[str, Any]) -> bool:
    """Reject exact, hash-equal, or same-family candidates as false negatives."""

    positive_text = normalize(str(positive.get("text", ""))).casefold()
    negative_text = normalize(str(negative.get("text", ""))).casefold()
    if positive_text == negative_text:
        return False
    positive_hash = str(positive.get("content_hash", ""))
    negative_hash = str(negative.get("content_hash", ""))
    if positive_hash and positive_hash == negative_hash:
        return False
    positive_family = str(positive.get("family_key", positive.get("lineage_key", "")))
    negative_family = str(negative.get("family_key", negative.get("lineage_key", "")))
    return positive_family != negative_family


def validate_query_record(value: Mapping[str, Any]) -> dict[str, Any]:
    text = normalize(str(value.get("text", "")))
    style = str(value.get("style", ""))
    if (
        not text
        or style not in STYLE_NAMES
        or not isinstance(value.get("answerable_from_passage"), bool)
    ):
        raise ValueError(
            "generated query must have text, one of four styles, and a boolean answerability"
        )
    return {
        "text": text,
        "style": style,
        "answerable_from_passage": bool(value["answerable_from_passage"]),
    }


def select_unique_passages(
    records: Sequence[Mapping[str, Any]],
    assignments: Mapping[str, str],
    manifest: Mapping[str, Any],
    quotes: Iterable[str],
) -> list[dict[str, Any]]:
    """Materialize train passages with the leakage guards applied."""

    selected: dict[str, dict[str, Any]] = {}
    for raw in records:
        if not qualifying_passage(raw):
            continue
        split = record_split(raw, assignments, manifest)
        if split != "train":
            continue
        assert_train_family(raw, assignments, manifest)
        record = dict(raw)
        record["content_hash"] = str(record.get("content_hash") or text_hash(str(record["text"])))
        leaked = passage_exposes_gold_quote(str(record["text"]), quotes)
        if leaked is not None:
            raise ValueError(f"train passage contains gold evidence quote: {record['lineage_key']}")
        selected.setdefault(record["content_hash"], record)
    return [selected[key] for key in sorted(selected)]


def union_rank_accepts(
    source_hash: str, rank_maps: Sequence[Mapping[str, int]], limit: int = 200
) -> bool:
    return any(source_hash in ranks and ranks[source_hash] <= limit for ranks in rank_maps)
