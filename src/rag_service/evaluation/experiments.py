"""Typed experiment configuration and reproducibility metadata.

This module deliberately does not run retrieval experiments.  It establishes
the foundation that later evaluation runners will use: one human-readable
config, one stable config hash, and one result artifact containing provenance.
"""

from __future__ import annotations

import hashlib
import json
import os
import platform
import sys
from datetime import UTC, datetime
from importlib import metadata
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict, Field


class ExperimentConfig(BaseModel):
    """The minimum provenance required for one reproducible experiment."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    experiment_id: str = Field(min_length=1)
    seed: int
    dataset: str = Field(min_length=1)
    system: str = Field(min_length=1)
    parameters: dict[str, Any] = Field(default_factory=dict)

    @property
    def config_hash(self) -> str:
        """Return the SHA-256 hash of the canonical config JSON."""

        encoded = _canonical_json(self.model_dump(mode="json")).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()


def load_experiment_config(path: str | Path) -> ExperimentConfig:
    """Load one YAML or JSON experiment config and validate it."""

    config_path = Path(path)
    with config_path.open(encoding="utf-8") as handle:
        raw = yaml.safe_load(handle)
    if not isinstance(raw, dict):
        raise ValueError(f"experiment config must contain a mapping: {config_path}")
    return ExperimentConfig.model_validate(raw)


def collect_runtime_provenance() -> dict[str, Any]:
    """Capture versions and hardware facts without making network calls."""

    package_names = (
        "evidence-rag",
        "fastapi",
        "mypy",
        "pydantic",
        "pydantic-settings",
        "pytest",
        "pytest-asyncio",
        "ruff",
        "uvicorn",
    )
    packages: dict[str, str | None] = {}
    for name in package_names:
        try:
            packages[name] = metadata.version(name)
        except metadata.PackageNotFoundError:
            packages[name] = None
    return {
        "captured_at_utc": datetime.now(UTC).isoformat(),
        "python": sys.version,
        "platform": platform.platform(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "cpu_count": os.cpu_count(),
        "packages": packages,
    }


def write_experiment_result(
    config: ExperimentConfig,
    metrics: dict[str, Any],
    *,
    results_dir: str | Path = "results",
    provenance: dict[str, Any] | None = None,
) -> Path:
    """Write a result named by its config hash and return its path."""

    output_dir = Path(results_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    result = {
        "config": config.model_dump(mode="json"),
        "config_hash": config.config_hash,
        "seed": config.seed,
        "metrics": metrics,
        "provenance": provenance or collect_runtime_provenance(),
    }
    output_path = output_dir / f"{config.config_hash}.json"
    output_path.write_text(_canonical_json(result) + "\n", encoding="utf-8")
    return output_path


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


__all__ = [
    "ExperimentConfig",
    "collect_runtime_provenance",
    "load_experiment_config",
    "write_experiment_result",
]
