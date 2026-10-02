import os
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from rag_service.evaluation import ExperimentConfig, load_experiment_config, write_experiment_result
from rag_service.settings import Settings


class SettingsTests(unittest.TestCase):
    def test_settings_read_rag_environment_aliases(self) -> None:
        with patch.dict(
            os.environ,
            {
                "RAG_ENV": "test",
                "RAG_LOG_LEVEL": "debug",
                "RAG_RETRIEVAL_TOP_K": "3",
                "RAG_RETRIEVAL_CANDIDATE_K": "7",
            },
            clear=False,
        ):
            settings = Settings()

        self.assertEqual(settings.environment, "test")
        self.assertEqual(settings.log_level, "DEBUG")
        self.assertEqual(settings.retrieval_top_k, 3)
        self.assertEqual(settings.retrieval_candidate_k, 7)

    def test_invalid_ranges_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            Settings(chunk_max_tokens=2, chunk_overlap_tokens=2)

    def test_config_hash_names_result_and_round_trips_yaml(self) -> None:
        config = ExperimentConfig(
            experiment_id="unit",
            seed=7,
            dataset="fixture",
            system="baseline",
            parameters={"top_k": 5},
        )
        with TemporaryDirectory() as directory:
            config_path = Path(directory) / "experiment.yaml"
            config_path.write_text(
                "experiment_id: unit\n"
                "seed: 7\n"
                "dataset: fixture\n"
                "system: baseline\n"
                "parameters:\n"
                "  top_k: 5\n",
                encoding="utf-8",
            )
            loaded = load_experiment_config(config_path)
            result_path = write_experiment_result(
                loaded,
                {"status": "not_run"},
                results_dir=Path(directory) / "results",
                provenance={"test": True},
            )
            self.assertTrue(result_path.exists())

        self.assertEqual(loaded.config_hash, config.config_hash)
        self.assertEqual(result_path.name, f"{config.config_hash}.json")


if __name__ == "__main__":
    unittest.main()
