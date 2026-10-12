import json
from pathlib import Path
from typing import Any

from rag_service.evaluation.experiments import ExperimentConfig
from rag_service.evaluation.phase4 import _find_cached_artifact


def test_find_cached_artifact_ignores_top_level_list(tmp_path: Path, capsys: Any) -> None:
    path = tmp_path / "phase4_comparisons.json"
    path.write_text(json.dumps([{"left": "default", "right": "bm25"}]))
    expected = ExperimentConfig(
        experiment_id="phase-4-evaluation",
        seed=42,
        dataset="data/eval/gold.jsonl",
        system="default",
        parameters={"pipeline": {}, "embedder_id": "hash-v1", "inputs": {}},
    )

    assert _find_cached_artifact(tmp_path, expected) is None
    assert "ignoring incompatible cache" in capsys.readouterr().out
