#!/usr/bin/env python3
"""Guarded parser-repair dry run, followed by explicitly requested artifact apply."""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

import psycopg
import yaml

from rag_service.benchmark.corpus import (
    SourceRecord,
    load_source_records,
    parse_postgresql_source,
    write_source_records,
)
from rag_service.benchmark.dataset import build_split_assignments, write_jsonl
from rag_service.benchmark.diffs import build_diffs
from rag_service.benchmark.families import family_map, manifest_errors, section_family
from rag_service.benchmark.gold import gold_version_map
from rag_service.ingestion.chunking import DeterministicChunker, content_hash_for_chunk

EXPECTED_QUOTE_IDS = {
    "draft-257b83c46f868ef6", "draft-2698580abdaeb4fb", "draft-05e120c03871ce0e",
    "draft-59e8d98dc1e8267d", "draft-9087662e522341da", "draft-aa8fc2079022d8f2",
    "draft-14d3ffdd0bfc1fc6", "draft-29bf0d3d09985e6f", "draft-434bc40422c18e75",
    "draft-6a52c545b09efc02", "draft-c606806c6ba4b0ef", "draft-580cf5be88985635",
    "draft-9c2802b2b594163e", "draft-54999895baea7983", "draft-54f1be3754a7cee9",
    "draft-917b1268426c767d",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def quote_span(before: str, after: str, start: int, end: int) -> tuple[str, int, int]:
    opcodes = difflib.SequenceMatcher(a=before, b=after, autojunk=False).get_opcodes()

    def translate(position: int, finish: bool) -> int:
        for tag, a, b, c, d in opcodes:
            if a <= position < b:
                return c + position - a if tag == "equal" else d if finish else c
            if position == a == b:
                return d if finish else c
        return len(after)

    left, right = translate(start, False), translate(end, True)
    return after[left:right], left, right


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--database-url")
    parser.add_argument("--refresh-new-record-inventory", action="store_true",
                        help="Refresh excluded record identity metadata only, after application")
    args = parser.parse_args()
    root = Path("data/eval")
    if args.refresh_new_record_inventory:
        report_path = root / "parser-repair-impact.json"
        report = json.loads(report_path.read_text())
        records = []
        inventory = []
        for version in ("pg-15", "pg-16", "pg-17"):
            impact: dict[str, Any] = {}
            records.extend(parse_postgresql_source(Path("data/processed/postgresql") / version,
                                                  version, impact=impact))
            inventory.extend(impact["new_records"])
        staged = Path("/tmp/omnirush/parser-repaired.inventory.jsonl")
        write_source_records(records, staged)
        if digest(staged) != report["source_sha256"] or len(inventory) != 607:
            raise RuntimeError("STOP: indexed source or excluded-record count changed")
        indexed = {(r.version, r.lineage_key) for r in records}
        if any((r["version"], r["lineage_key"]) in indexed for r in inventory):
            raise RuntimeError("STOP: restored-record identity collides with indexed record")
        report["new_records"] = inventory
        save(report_path, report)
        print("Recorded 607 excluded identities; indexed corpus unchanged")
        return
    if not args.database_url:
        parser.error("--database-url is required for the embedding dry run")
    full = Path("data/processed/source_sections.full.jsonl")
    old = load_source_records(full)
    old_map = {(r.version, r.lineage_key): r for r in old}
    review_path = root / "reviewed.jsonl"
    review_hash = digest(review_path)
    candidate_hash = digest(root / "candidates.jsonl")
    rows = [json.loads(line) for line in (root / "candidates.jsonl").read_text().splitlines()]
    old_splits = json.loads((root / "splits.json").read_text())
    previous_manifest = json.loads((root / "section_families.json").read_text())
    new: list[SourceRecord] = []
    additions = []
    unresolved = {}
    for version in ("pg-15", "pg-16", "pg-17"):
        impact: dict[str, Any] = {}
        new.extend(parse_postgresql_source(Path("data/processed/postgresql") / version,
                                           version, impact=impact))
        additions.extend(impact["new_records"])
        unresolved[version] = impact["unresolved_references"]
    new_map = {(r.version, r.lineage_key): r for r in new}
    guards = []
    if not old_map.keys() <= new_map.keys():
        guards.append("existing lineage key removed")
    for key, record in old_map.items():
        if key not in new_map:
            continue
        updated = new_map[key]
        if (record.section_id != updated.section_id
                or section_family(record) != section_family(updated)
                or (record.source_file, record.source_line, record.kind) !=
                   (updated.source_file, updated.source_line, updated.kind)):
            guards.append(f"existing record identity changed: {key}")
    mapping = {key: value["family_key"] for key, value in previous_manifest["lineages"].items()}
    mapping.update(family_map(new))
    assignments = build_split_assignments(new, old_splits["assignments"], lineage_families=mapping)
    if any(assignments.get(key) != value for key, value in old_splits["assignments"].items()):
        guards.append("existing split assignment changed")
    manifest = json.loads(json.dumps(previous_manifest))
    for record in new:
        if record.lineage_key in previous_manifest["lineages"]:
            continue
        entry = manifest["lineages"].setdefault(record.lineage_key, {
            "family_key": section_family(record), "section_id": record.section_id,
            "section_lineage": record.metadata.get("section_lineage"),
            "active": True, "versions": [], "kinds": [],
        })
        entry["versions"] = sorted(set(entry["versions"]) | {record.version})
        entry["kinds"] = sorted(set(entry["kinds"]) | {record.kind})
    manifest.update(source_records=len(new), active_lineages=len({r.lineage_key for r in new}),
                    active_families=len({section_family(r) for r in new}))
    guards.extend(manifest_errors(manifest, assignments, new))
    gold = gold_version_map(new)
    updated_rows = []
    quote_changes = []
    acl_titles = yaml.safe_load(Path("data/acl_demo.yaml").read_text())["restricted_section_titles"]
    acl_ok = 0
    for row in rows:
        updated_row = dict(row)
        spans = []
        changes = []
        for span in row["evidence_spans"]:
            key = span["version"], span["lineage_key"]
            before, after = old_map[key], new_map[key]
            if span["quote"] in after.text:
                quote = span["quote"]
                # Use the aligned source position when possible, avoiding a
                # same-sentence occurrence from a different parameter.
                aligned, start, end = quote_span(before.text, after.text,
                                                 span["start_char"], span["end_char"])
                if aligned != quote:
                    start = after.text.index(quote)
                    end = start + len(quote)
            else:
                quote, start, end = quote_span(before.text, after.text,
                                               span["start_char"], span["end_char"])
                changes.append({"lineage_key": span["lineage_key"], "version": span["version"],
                                "old_quote": span["quote"], "new_quote": quote})
            spans.append({**span, "quote": quote, "start_char": start, "end_char": end,
                          "section_path": list(after.section_path),
                          "gold_versions": gold[span["lineage_key"], span["version"]]
                          if row["version_independent"] else []})
        updated_row.update(evidence_spans=spans, evidence_quote=(
            [s["quote"] for s in spans] if len(spans) > 1 else spans[0]["quote"] if spans else ""))
        if row["version_independent"]:
            updated_row["gold_versions"] = sorted(set.intersection(
                *(set(s["gold_versions"]) for s in spans)))
        if changes:
            quote_changes.append({"id": row["id"], "changes": changes})
        if row["type"] == "acl":
            if all(any(title.lower() in " / ".join(s["section_path"]).lower()
                       for title in acl_titles) for s in spans):
                acl_ok += 1
            else:
                guards.append(f"ACL no longer restricted: {row['id']}")
        updated_rows.append(updated_row)
    if {row["id"] for row in quote_changes} != EXPECTED_QUOTE_IDS:
        guards.append("changed quote IDs differ from the approved 16")
    immutable = ("id", "question", "expected_answer", "lineage_key", "split")
    if not all(all(before[field] == after[field] for field in immutable)
               and [s["lineage_key"] for s in before["evidence_spans"]] ==
                   [s["lineage_key"] for s in after["evidence_spans"]]
               for before, after in zip(rows, updated_rows, strict=True)):
        guards.append("candidate identity/question/answer/lineage changed")
    staged = Path("/tmp/omnirush/parser-repaired.full.jsonl")
    write_source_records(new, staged)
    manifest["source_sha256"] = digest(staged)
    chunker = DeterministicChunker(max_tokens=220, overlap_tokens=35)
    with psycopg.connect(args.database_url) as conn:
        conn.execute("SET TRANSACTION READ ONLY")
        if conn.execute("SELECT current_database()").fetchone()[0] != "evidence_rag_eval":
            raise ValueError("Dry run requires evidence_rag_eval")
        cached = {r[0] for r in conn.execute(
            "SELECT content_hash FROM embeddings WHERE embedder_id=%s", ("bge-small-en-v1.5",))}
    per_version = {}
    for version in ("pg-15", "pg-16", "pg-17"):
        records = [r for r in new if r.version == version]
        windows = [w for r in records for w in chunker._structured_windows(r.text, r.kind)]
        hashes = {content_hash_for_chunk(text, kind) for kind, text in windows}
        changed_chunks = metadata_chunks = added_chunks = 0
        for record in records:
            prior = old_map.get((version, record.lineage_key))
            after = chunker._structured_windows(record.text, record.kind)
            before = chunker._structured_windows(prior.text, prior.kind) if prior else []
            changed_chunks += sum(left != right for left, right in zip(before, after, strict=False))
            added_chunks += max(0, len(after) - len(before))
            if prior and (prior.title, prior.section_path, prior.caption) != (
                record.title, record.section_path, record.caption
            ):
                metadata_chunks += len(after)
        per_version[version] = {
            "documents": 1, "sections": len(records), "chunks": len(windows),
            "table_chunks": sum(kind == "table" for kind, _ in windows),
            "code_chunks": sum(kind == "code" for kind, _ in windows),
            "changed_chunk_text": changed_chunks, "added_chunks": added_chunks,
            "changed_display_metadata_chunks": metadata_chunks,
            "embeddings_computed_estimate": len(hashes - cached),
            "embeddings_reused_estimate": len(hashes & cached),
        }
        cached.update(hashes)
    distribution = {label: sum(low <= r["characters"] < high for r in additions)
                    for label, low, high in [("under_50", 0, 50), ("50_99", 50, 100),
                                             ("100_299", 100, 300), ("300_1499", 300, 1500),
                                             ("1500_plus", 1500, 10**9)]}
    report = {
        "guards": guards, "baseline": "6346c8f", "source_sha256": manifest["source_sha256"],
        "existing_records": len(old), "repaired_records": len(new),
        "previously_empty_records": len(additions), "new_record_length_distribution": distribution,
        "new_record_min_chars": min(r["characters"] for r in additions),
        "new_record_max_chars": max(r["characters"] for r in additions),
        "excluded_under_50": sum(r["characters"] < 50 for r in additions),
        "excluded_reference_only": sum(r["reference_only"] for r in additions),
        "excluded_union": sum(r["excluded"] for r in additions),
        "indexed_new_records": sum(not r["excluded"] for r in additions),
        "new_records": additions, "unresolved_references": unresolved,
        "per_version": per_version, "quote_changes": quote_changes,
        "total_embeddings_computed_estimate": sum(
            values["embeddings_computed_estimate"] for values in per_version.values()),
        "changed_quote_ids": [row["id"] for row in quote_changes],
        "acl_restricted_candidates": acl_ok, "reviews_sha256": review_hash,
        "baseline_candidates_sha256": candidate_hash,
        "existing_identity_and_assignments_preserved": not guards,
        "manifest_existing_entries_unchanged": all(
            manifest["lineages"][key] == value
            for key, value in previous_manifest["lineages"].items()),
    }
    save(Path("/tmp/omnirush/identity-preserved-parser-impact.json"), report)
    print(json.dumps({k: v for k, v in report.items()
                      if k not in {"quote_changes", "new_records", "unresolved_references"}},
                     indent=2, sort_keys=True))
    if guards:
        raise RuntimeError("STOP: " + guards[0])
    if report["total_embeddings_computed_estimate"] >= 10000:
        raise RuntimeError("STOP: embedding scope exceeds the approved limit")
    if digest(review_path) != review_hash:
        raise RuntimeError("STOP: review file changed")
    if digest(root / "candidates.jsonl") != candidate_hash:
        raise RuntimeError("STOP: candidate file changed during dry run")
    if not args.apply:
        return
    # All guards passed before any benchmark artifacts are replaced.
    write_source_records(new, full)
    write_jsonl(updated_rows, root / "candidates.jsonl")
    save(root / "section_families.json", manifest)
    blind = sorted(key for key, split in assignments.items() if split == "blind")
    save(root / "splits.json", {**old_splits, "assignments": assignments,
                               "blind_pool": blind, "counts": dict(Counter(assignments.values())),
                               "splits": {split: sorted(k for k, v in assignments.items()
                                                        if v == split)
                                          for split in ("train", "dev", "test", "blind")}})
    needed = {(s["lineage_key"], version) for row in updated_rows for s in row["evidence_spans"]
              for version in {s["version"], *s.get("gold_versions", [])}}
    compact_old = load_source_records(root / "source_sections.jsonl")
    compact = []
    blind_seen = set()
    for record in compact_old:
        if assignments.get(record.lineage_key) == "blind":
            compact.append(new_map.get((record.version, record.lineage_key), record))
            blind_seen.add(record.lineage_key)
    compact.extend(record for record in new if (record.lineage_key, record.version) in needed)
    for record in new:
        if assignments.get(record.lineage_key) == "blind" and record.lineage_key not in blind_seen:
            compact.append(record)
            blind_seen.add(record.lineage_key)
    write_source_records(compact, root / "source_sections.jsonl")
    diffs, diff_stats = build_diffs(new)
    write_jsonl(diffs, root / "diffs.jsonl")
    stats = json.loads((root / "benchmark_stats.json").read_text())
    stats.update(source_records_per_version=dict(Counter(r.version for r in new)), diffs=diff_stats,
                 validation_source_records=len(compact), parser_repair="parser-repair-impact.json")
    save(root / "benchmark_stats.json", stats)
    migration = json.loads((root / "split-migration.json").read_text())
    migration.setdefault("parser_extensions", []).append({
        "source_sha256": manifest["source_sha256"], "added_assignments": {
            key: split for key, split in assignments.items()
            if key not in old_splits["assignments"]},
        "existing_entries_and_assignments_unchanged": True,
    })
    save(root / "split-migration.json", migration)
    save(root / "parser-repair-impact.json", report)
    output = ["# Evidence changes requiring re-review", ""]
    for row in quote_changes:
        output.extend([f"## {row['id']}", ""])
        for change in row["changes"]:
            output.extend([f"{change['version']} / `{change['lineage_key']}`", "",
                           "**Old quote**", "```text", change["old_quote"], "```", "",
                           "**New quote**", "```text", change["new_quote"], "```", ""])
    Path("docs/phase-3-evidence-changes.md").write_text("\n".join(output))
    print("Applied guarded artifacts; reviewed.jsonl was not edited")


if __name__ == "__main__":
    main()
