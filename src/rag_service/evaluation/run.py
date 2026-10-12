"""Reproducible evaluation artifacts and the Phase 4 host/cached runners."""

from __future__ import annotations

import argparse
from pathlib import Path

from .experiments import load_experiment_config, write_experiment_result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path)
    parser.add_argument("--results-dir", default=Path("results"), type=Path)
    parser.add_argument("--metadata-prefix", action="store_true")
    parser.add_argument("--bge-base", action="store_true")
    parser.add_argument("--chunk-size", action="store_true")
    parser.add_argument("--scifact", action="store_true")
    parser.add_argument("--refresh", action="store_true")
    parser.add_argument("--smoke", action="store_true",
                        help="run every selected arm on three gold questions only")
    parser.add_argument("--preflight-only", action="store_true")
    parser.add_argument("--check-cache", type=Path)
    args = parser.parse_args()
    if args.check_cache:
        from .phase4 import check_cache

        check_cache(args.check_cache)
        return
    if not args.config:
        parser.error("--config is required unless --check-cache is used")
    config = load_experiment_config(args.config)
    if config.system == "phase4-suite":
        from .phase4 import execute

        flags = {flag for flag in ("metadata-prefix", "bge-base", "chunk-size", "scifact")
                 if getattr(args, flag.replace("-", "_"))}
        try:
            result_path = execute(config, args.results_dir, flags, refresh=args.refresh,
                                  preflight_only=args.preflight_only, smoke_only=args.smoke)
        except Exception as exc:
            raise SystemExit(f"Phase 4 stopped: {type(exc).__name__}: {exc}") from exc
        print(result_path.resolve())
        return
    result_path = write_experiment_result(config, {}, results_dir=args.results_dir)
    print(result_path)


if __name__ == "__main__":
    main()
