#!/usr/bin/env python3
"""Display eligible corpus passages or diff metadata for manual drafting.

This tool selects source text only. It never constructs questions or answers.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from rag_service.benchmark.corpus import load_source_records
from rag_service.benchmark.drafts import DraftImporter


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=["diffs", "catalog", "passages"], default="passages")
    parser.add_argument("--filter", default="")
    parser.add_argument("--kind", default="")
    parser.add_argument("--stable", action="store_true")
    parser.add_argument("--version", default="pg-15")
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--limit", type=int, default=25)
    parser.add_argument("--chars", type=int, default=1500)
    parser.add_argument("--contains", default="")
    args = parser.parse_args()
    root = Path("data/eval")
    records = load_source_records("data/processed/source_sections.full.jsonl")
    assignments = json.loads((root / "splits.json").read_text())["assignments"]
    diffs = [json.loads(line) for line in (root / "diffs.jsonl").read_text().splitlines()]
    importer = DraftImporter(records, assignments, diffs)
    if args.mode == "diffs":
        eligible = [d for d in diffs if assignments.get(d["lineage_key"]) in {"dev", "test"}
                    and any(c["kind"] != "text_changed" for c in d["changes"])
                    and args.filter in json.dumps(d["changes"])]
        print(f"Eligible diffs: {len(eligible)}")
        for d in eligible[args.offset:args.offset + args.limit]:
            print(d["id"], assignments[d["lineage_key"]], d["section_path"])
            for c in d["changes"]:
                print(json.dumps(c)[:args.chars])
    else:
        eligible_records = [r for r in records
                            if assignments.get(r.lineage_key) in {"dev", "test"}
                            and r.version == args.version
                            and (not args.stable or r.lineage_key in importer.stable)
                            and (not args.kind or r.kind == args.kind)
                            and args.filter.casefold() in (
                                r.lineage_key + " " + " / ".join(r.section_path)).casefold()
                            and args.contains.casefold() in r.text.casefold()]
        print(f"Eligible records: {len(eligible_records)}")
        for r in eligible_records[args.offset:args.offset + args.limit]:
            print(f"\n{r.lineage_key} {r.version} {assignments[r.lineage_key]} "
                  f"{r.kind} chars={len(r.text)} stable={r.lineage_key in importer.stable} "
                  f"{' / '.join(r.section_path)}")
            if args.mode == "passages":
                start = max(0, r.text.casefold().find(args.contains.casefold()) - 150)
                print(r.text[start:start + args.chars])


if __name__ == "__main__":
    main()
