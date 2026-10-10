"""Section-family identity and split isolation, independent of section titles."""

from __future__ import annotations

from collections import Counter, defaultdict
from collections.abc import Iterable, Mapping
from typing import Any

from .corpus import SourceRecord


def section_family(record: SourceRecord) -> str:
    return str(record.metadata.get("section_lineage") or "pg-section:" + record.section_id)


def family_map(records: Iterable[SourceRecord]) -> dict[str, str]:
    result: dict[str, str] = {}
    for record in records:
        family = section_family(record)
        if record.lineage_key in result and result[record.lineage_key] != family:
            raise ValueError(f"conflicting family identity: {record.lineage_key}")
        result[record.lineage_key] = family
    return result


def question_lineages(row: Mapping[str, Any]) -> set[str]:
    primary = str(row.get("lineage_key", ""))
    return {primary, *(str(s.get("lineage_key", primary))
                       for s in row.get("evidence_spans", []))} - {""}


def connected_families(
    families: Iterable[str], connections: Iterable[Iterable[str]],
) -> list[set[str]]:
    parents = {family: family for family in families}

    def find(family: str) -> str:
        while parents[family] != family:
            parents[family] = parents[parents[family]]
            family = parents[family]
        return family

    for connection in connections:
        values = sorted(set(connection))
        for family in values[1:]:
            left, right = find(values[0]), find(family)
            if left != right:
                parents[max(left, right)] = min(left, right)
    groups: dict[str, set[str]] = defaultdict(set)
    for family in sorted(parents):
        groups[find(family)].add(family)
    return list(groups.values())


def isolation_errors(
    assignments: Mapping[str, str], lineage_families: Mapping[str, str],
    connections: Iterable[Iterable[str]] = (), exposed: Iterable[str] = (),
) -> list[str]:
    errors = []
    groups: dict[str, set[str]] = defaultdict(set)
    for key, split in assignments.items():
        if key not in lineage_families:
            errors.append(f"lineage missing family metadata: {key}")
        else:
            groups[lineage_families[key]].add(split)
    for family, splits in groups.items():
        if len(splits) != 1:
            errors.append(f"section family spans splits: {family}")
    for connection in connections:
        values = set(connection)
        if not values <= groups.keys():
            errors.append("connected family missing from assignments")
        elif len(set().union(*(groups[f] for f in values))) != 1:
            errors.append(f"multi-hop family component spans splits: {sorted(values)}")
    for family in exposed:
        if "blind" in groups.get(family, set()):
            errors.append(f"exposed question family in blind: {family}")
    return errors


def resolve_migration(
    previous: Mapping[str, str], lineage_families: Mapping[str, str],
    protected: Mapping[str, set[str]], exposed: set[str],
    connections: Iterable[Iterable[str]],
) -> tuple[dict[str, str], dict[str, str]]:
    """Apply the owner's one-time approved rules, without changing any question."""
    members: dict[str, set[str]] = defaultdict(set)
    for key in previous:
        members[lineage_families[key]].add(key)
    assignments = {}
    decisions = {}
    rank = {"dev": 0, "test": 1, "train": 2}
    for component in connected_families(members, connections):
        keys = set().union(*(members[f] for f in component))
        counts = Counter(previous[k] for k in keys)
        labels = set(counts)
        if component & protected.keys():
            labels |= set().union(*(protected.get(f, set()) for f in component))
            target = "dev" if "dev" in labels else "test"
            reason = "candidate/review component"
        elif component & exposed:
            target = "dev" if "dev" in labels else "test"
            reason = "historical question exposure"
        elif "blind" in labels:
            target, reason = "blind", "retain unexposed blind family"
        elif {"dev", "test"} <= labels:
            target, reason = "dev", "dev/test conflict prefers dev"
        else:
            target = min(counts, key=lambda split: (-counts[split], rank[split]))
            reason = "minimum member changes; ties dev/test/train"
        for key in keys:
            assignments[key] = target
        for family in component:
            decisions[family] = reason
    return assignments, decisions


def manifest_errors(
    manifest: Mapping[str, Any], assignments: Mapping[str, str], records: list[SourceRecord],
) -> list[str]:
    entries = manifest["lineages"]
    mapping = {key: value["family_key"] for key, value in entries.items()}
    errors = isolation_errors(assignments, mapping, manifest.get("components", []),
                              manifest.get("exposed_families", []))
    if set(entries) != set(assignments):
        errors.append("family manifest does not cover exactly the assigned lineages")
    for key, value in entries.items():
        expected = value.get("section_lineage") or "pg-section:" + value["section_id"]
        if expected != value["family_key"]:
            errors.append(f"manifest section identity mismatch: {key}")
    for record in records:
        entry = entries.get(record.lineage_key)
        if not entry or section_family(record) != entry["family_key"]:
            errors.append(f"source record family mismatch: {record.lineage_key}")
        elif record.version not in entry["versions"] or record.kind not in entry["kinds"]:
            errors.append(f"source record absent from family manifest: {record.lineage_key}")
    active = [entry for entry in entries.values() if entry["active"]]
    if len(active) != manifest["active_lineages"]:
        errors.append("manifest active lineage count mismatch")
    if len({entry["family_key"] for entry in active}) != manifest["active_families"]:
        errors.append("manifest active family count mismatch")
    return errors


def refresh_manifest(
    records: list[SourceRecord], assignments: dict[str, str], previous: dict[str, Any],
    source_sha256: str,
) -> dict[str, Any]:
    entries = {key: {**value, "active": False} for key, value in previous["lineages"].items()
               if key in assignments}
    current: set[str] = set()
    for record in records:
        key = record.lineage_key
        if key not in current:
            entries[key] = {"family_key": section_family(record), "section_id": record.section_id,
                            "section_lineage": record.metadata.get("section_lineage"),
                            "versions": [], "kinds": [], "active": True}
            current.add(key)
        entry = entries[key]
        entry["versions"] = sorted(set(entry["versions"]) | {record.version})
        entry["kinds"] = sorted(set(entry["kinds"]) | {record.kind})
    return {**previous, "lineages": entries, "source_sha256": source_sha256,
            "source_records": len(records), "active_lineages": len(current),
            "active_families": len({section_family(r) for r in records})}
