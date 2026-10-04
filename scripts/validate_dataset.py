#!/usr/bin/env python3
"""CI entry point for the Phase 3 dataset validator."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from rag_service.benchmark.validation import validate_dataset


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, default=Path("data/eval/candidates.jsonl"))
    parser.add_argument("--source", type=Path, default=Path("data/eval/source_sections.jsonl"))
    parser.add_argument("--splits", type=Path, default=Path("data/eval/splits.json"))
    parser.add_argument("--allow-incomplete", action="store_true")
    args = parser.parse_args()
    result = validate_dataset(
        args.dataset,
        args.source,
        args.splits,
        require_targets=not args.allow_incomplete,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
