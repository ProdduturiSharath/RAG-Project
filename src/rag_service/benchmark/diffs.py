"""Mine answer-changing and table changes from aligned documentation sections."""

from __future__ import annotations

import difflib
import re
from collections import Counter, defaultdict
from typing import Any

from .corpus import SourceRecord

_IDENTIFIER_RE = re.compile(
    r"\b[A-Za-z][A-Za-z0-9_]*(?:\.[A-Za-z][A-Za-z0-9_]*)*(?:\(\))?\b"
)
_DEFAULT_RE = re.compile(
    r"\b(?:default(?:\s+value)?\s*(?:is|=|:)|defaults?\s+to)\s*"
    r"[`'\"]?([A-Za-z0-9_.-]+)",
    re.I,
)
_PARAMETER_HINTS = ("_", ".", "pg_", "wal", "work_mem", "shared_", "max_")
_SETTING_RE = re.compile(
    r"\b([a-z][a-z0-9_]+)\s+\(\s*(?:integer|boolean|enum|string|floating point)\s*\)"
)


def _group(records: list[SourceRecord]) -> dict[str, dict[str, list[SourceRecord]]]:
    grouped: dict[str, dict[str, list[SourceRecord]]] = defaultdict(lambda: defaultdict(list))
    for record in records:
        grouped[record.lineage_key][record.version].append(record)
    return grouped


def _combined(values: list[SourceRecord]) -> str:
    ordered = sorted(values, key=lambda value: (value.kind, value.source_line))
    return "\n".join(item.text for item in ordered)


def _quote_for_change(before: str, after: str) -> tuple[str, str]:
    old_lines = before.splitlines() or [before]
    new_lines = after.splitlines() or [after]
    matcher = difflib.SequenceMatcher(a=old_lines, b=new_lines)
    for tag, old_start, old_end, new_start, new_end in matcher.get_opcodes():
        if tag != "equal":
            old_quote = "\n".join(old_lines[old_start:old_end]).strip() or old_lines[0]
            new_quote = "\n".join(new_lines[new_start:new_end]).strip() or new_lines[0]
            return old_quote, new_quote
    return before.strip(), after.strip()


def _identifiers(text: str) -> set[str]:
    values: set[str] = set()
    for match in _IDENTIFIER_RE.finditer(text):
        value = match.group(0)
        lowered = value.lower()
        if any(hint in lowered for hint in _PARAMETER_HINTS) or value.endswith("()"):
            values.add(value)
    return values


def _default_changes(before: str, after: str) -> list[dict[str, str]]:
    def values(text: str) -> dict[str, str]:
        found: dict[str, str] = {}
        for match in _DEFAULT_RE.finditer(text):
            headings = list(_SETTING_RE.finditer(text[:match.start()]))
            if headings:
                found[headings[-1].group(1)] = match.group(1).rstrip(".")
                continue
            context = _IDENTIFIER_RE.findall(text[:match.start()])
            names = [
                value for value in context
                if any(hint in value.lower() for hint in _PARAMETER_HINTS)
            ]
            if names:
                found[names[-1]] = match.group(1).rstrip(".")
        return found

    old = values(before)
    new = values(after)
    changes: list[dict[str, str]] = []
    for key in sorted(set(old) & set(new)):
        if old.get(key) != new.get(key):
            changes.append(
                {
                    "kind": "changed_default",
                    "name": key[:80],
                    "before": old.get(key, "removed"),
                    "after": new.get(key, "added"),
                }
            )
    return changes


def _table_changes(old: list[SourceRecord], new: list[SourceRecord]) -> list[dict[str, str]]:
    old_rows = {
        " | ".join(row): row
        for record in old
        for row in record.table_rows
        if any(cell.strip() for cell in row)
    }
    new_rows = {
        " | ".join(row): row
        for record in new
        for row in record.table_rows
        if any(cell.strip() for cell in row)
    }
    changes: list[dict[str, str]] = []
    for row in sorted(set(old_rows) - set(new_rows)):
        changes.append({"kind": "table_row_removed", "name": row, "before": row, "after": ""})
    for row in sorted(set(new_rows) - set(old_rows)):
        changes.append({"kind": "table_row_added", "name": row, "before": "", "after": row})
    return changes


def _parameter_changes(before: str, after: str) -> list[dict[str, str]]:
    old = _contextual_identifiers(before)
    new = _contextual_identifiers(after)
    removed = sorted(old - new)
    added = sorted(new - old)
    changes: list[dict[str, str]] = []
    for name in removed:
        changes.append({"kind": "parameter_removed", "name": name, "before": name, "after": ""})
    for name in added:
        changes.append({"kind": "parameter_added", "name": name, "before": "", "after": name})
    if len(removed) == 1 and len(added) == 1:
        changes.append(
            {
                "kind": "parameter_renamed",
                "name": added[0],
                "before": removed[0],
                "after": added[0],
            }
        )
    return changes


def _contextual_identifiers(text: str) -> set[str]:
    values: set[str] = set(_SETTING_RE.findall(text))
    context_words = (
        "parameter",
        "setting",
        "configuration",
        "default",
        "function",
        "argument",
    )
    for match in _IDENTIFIER_RE.finditer(text):
        value = match.group(0)
        lowered = value.lower()
        context = text[max(0, match.start() - 90):match.end() + 90].lower()
        if (
            (any(hint in lowered for hint in _PARAMETER_HINTS) or value.endswith("()"))
            and any(word in context for word in context_words)
        ):
            values.add(value)
    return values


def build_diffs(
    records: list[SourceRecord],
    versions: tuple[str, ...] = ("pg-15", "pg-16", "pg-17"),
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Return one JSON-serializable record for each changed lineage/version pair."""

    grouped = _group(records)
    diffs: list[dict[str, Any]] = []
    matched = 0
    changed = 0
    change_kinds: Counter[str] = Counter()
    for left, right in zip(versions, versions[1:], strict=False):
        for lineage, by_version in sorted(grouped.items()):
            if left not in by_version or right not in by_version:
                continue
            matched += 1
            before = _combined(by_version[left])
            after = _combined(by_version[right])
            if before == after:
                continue
            changed += 1
            old_quote, new_quote = _quote_for_change(before, after)
            changes = _default_changes(before, after)
            changes.extend(_parameter_changes(before, after))
            changes.extend(_table_changes(by_version[left], by_version[right]))
            if not changes:
                changes.append(
                    {
                        "kind": "text_changed",
                        "name": "section text",
                        "before": old_quote,
                        "after": new_quote,
                    }
                )
            change_kinds.update(str(change["kind"]) for change in changes)
            diffs.append(
                {
                    "id": f"diff-{left}-{right}-{lineage}",
                    "lineage_key": lineage,
                    "section_path": list(by_version[left][0].section_path),
                    "from_version": left,
                    "to_version": right,
                    "changes": changes,
                    "evidence": [
                        {
                            "version": left,
                            "quote": old_quote,
                            "source_file": by_version[left][0].source_file,
                            "source_line": by_version[left][0].source_line,
                        },
                        {
                            "version": right,
                            "quote": new_quote,
                            "source_file": by_version[right][0].source_file,
                            "source_line": by_version[right][0].source_line,
                        },
                    ],
                }
            )
    stats = {
        "lineages_total": len(grouped),
        "lineages_matched": matched,
        "lineages_changed": changed,
        "diff_records": len(diffs),
        "change_kinds": dict(sorted(change_kinds.items())),
    }
    return diffs, stats


__all__ = ["build_diffs"]
