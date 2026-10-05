"""Persisted lineage splitting and JSONL serialization; no question generation."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from .corpus import SourceRecord
from .families import family_map, isolation_errors


def build_split_assignments(
    records: Iterable[SourceRecord], previous: dict[str, str] | None = None,
    *, lineage_families: dict[str, str] | None = None,
) -> dict[str, str]:
    """Preserve family decisions; new blocks/versions inherit their section split."""
    records = list(records)
    previous = previous or {}
    mapping = dict(lineage_families or {})
    mapping.update(family_map(records))
    for key in previous:
        mapping.setdefault(key, key)
    errors = isolation_errors(previous, mapping)
    if errors:
        raise ValueError("family split migration required: " + errors[0])
    family_splits = {mapping[key]: split for key, split in previous.items()}
    assignments = {key: split for key, split in previous.items() if split == "blind"}
    for lineage in sorted({record.lineage_key for record in records}):
        family = mapping[lineage]
        bucket = int(hashlib.sha256(family.encode()).hexdigest()[:8], 16) % 100
        if family in family_splits:
            assignments[lineage] = family_splits[family]
        elif previous:
            # A refresh must never enlarge the owner's blind pool.
            assignments[lineage] = ("train", "dev", "test")[bucket % 3]
        else:
            assignments[lineage] = (
                "blind" if bucket < 10 else "train" if bucket < 40
                else "dev" if bucket < 70 else "test"
            )
        family_splits[family] = assignments[lineage]
    return assignments


def write_jsonl(rows: Iterable[dict[str, Any]], path: str | Path) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
