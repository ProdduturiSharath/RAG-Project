"""Persisted lineage splitting and JSONL serialization; no question generation."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from .corpus import SourceRecord


def build_split_assignments(
    records: Iterable[SourceRecord], previous: dict[str, str] | None = None,
) -> dict[str, str]:
    """Preserve surviving assignments and the blind pool, including retired keys."""
    previous = previous or {}
    assignments = {key: split for key, split in previous.items() if split == "blind"}
    for lineage in sorted({record.lineage_key for record in records}):
        bucket = int(hashlib.sha256(lineage.encode()).hexdigest()[:8], 16) % 100
        if lineage in previous:
            assignments[lineage] = previous[lineage]
        elif previous:
            # A refresh must never enlarge the owner's blind pool.
            assignments[lineage] = ("train", "dev", "test")[bucket % 3]
        else:
            assignments[lineage] = (
                "blind" if bucket < 10 else "train" if bucket < 40
                else "dev" if bucket < 70 else "test"
            )
    return assignments


def write_jsonl(rows: Iterable[dict[str, Any]], path: str | Path) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
