"""CLI foundation for reproducible evaluation result artifacts."""

from __future__ import annotations

import argparse
from pathlib import Path

from .experiments import load_experiment_config, write_experiment_result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--results-dir", default=Path("results"), type=Path)
    args = parser.parse_args()
    config = load_experiment_config(args.config)
    result_path = write_experiment_result(config, {}, results_dir=args.results_dir)
    print(result_path)


if __name__ == "__main__":
    main()
