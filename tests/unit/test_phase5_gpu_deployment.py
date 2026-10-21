"""Offline regression tests for RunPod deployment, resume, and artifact safety."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import sys
import tarfile
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import numpy as np
import pytest

from scripts import phase5_gpu as gpu


@pytest.fixture
def inputs(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setattr(gpu, "ROOT", tmp_path)
    train = tmp_path / "data/train"
    train.mkdir(parents=True)
    row = {"content_hash": "p1", "text": "A passage.", "kind": "text"}
    for name, rows in (
        ("train_passages", [row]), ("corpus_texts", [row]),
        ("train_queries", [{"query_id": f"q{i}", "question": "What?",
                            "positive_content_hash": "p1"} for i in range(2937)]),
    ):
        with gzip.open(train / f"{name}.jsonl.gz", "wt") as stream:
            stream.write("\n".join(json.dumps(value) for value in rows))
    evaluation = tmp_path / "data/eval"
    evaluation.mkdir()
    (evaluation / "gold.jsonl").write_text(
        "\n".join(json.dumps({"id": str(i), "question": "What?"}) for i in range(212))
    )
    (evaluation / "section_families.json").write_text('{"lineages": {}}')
    return train


def test_inputs_accept_2937_queries_without_results(inputs: Path) -> None:
    passages, corpus, queries, gold, _, fingerprints = gpu.load_inputs(inputs)
    assert (len(passages), len(corpus), len(queries), len(gold)) == (1, 1, 2937, 212)
    assert len(fingerprints) == 5
    assert not (gpu.ROOT / "results").exists()


def test_missing_inputs_fail_before_install(inputs: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    (inputs / "train_queries.jsonl.gz").unlink()
    monkeypatch.setattr(gpu, "install_deps", lambda: pytest.fail("must not install yet"))
    with pytest.raises(RuntimeError, match="train_queries"):
        gpu.run(argparse.Namespace(input=str(inputs)))


def test_check_inputs_is_offline(inputs: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(gpu, "install_deps", lambda: pytest.fail("must not install"))
    assert gpu.run(argparse.Namespace(input=str(inputs), check_inputs=True)) == 0


@pytest.mark.parametrize("failure", [False, True])
@pytest.mark.parametrize("flag", [None, "--no-stop", "--stop-on-exit"])
def test_pod_stop_requires_explicit_opt_in(
    monkeypatch: pytest.MonkeyPatch, flag: str | None, failure: bool
) -> None:
    stopped: list[bool] = []
    monkeypatch.setattr(sys, "argv", ["phase5_gpu.py", *([flag] if flag else [])])
    monkeypatch.setattr(gpu, "stop_pod", lambda: stopped.append(True))

    def fake_run(args: Any) -> int:
        if failure:
            raise ValueError("training failed")
        return 0

    monkeypatch.setattr(gpu, "run", fake_run)
    if failure:
        with pytest.raises(ValueError, match="training failed"):
            gpu.main()
    else:
        assert gpu.main() == 0
    assert stopped == ([True] if flag == "--stop-on-exit" else [])


def test_package_is_complete_and_checksum_matches(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(gpu, "ROOT", tmp_path)
    output = tmp_path / "custom-output"
    output.mkdir()
    (output / "vector.npy").write_bytes(b"example-vector")
    gpu.package(output, {"train_queries": 2937})
    archive = tmp_path / "phase5_outputs.tar.gz"
    assert archive.is_file()
    with tarfile.open(archive) as tar:
        assert "phase5_outputs/run_summary.json" in tar.getnames()
        assert "phase5_outputs/vector.npy" in tar.getnames()
    expected = hashlib.sha256(archive.read_bytes()).hexdigest()
    assert archive.with_name(archive.name + ".sha256").read_text() == (
        f"{expected}  phase5_outputs.tar.gz\n"
    )


def test_resume_requires_indexes_as_well_as_vectors(tmp_path: Path) -> None:
    vectors = tmp_path / "vectors"
    vectors.mkdir()
    for suffix in ("", "-queries", "-eval-queries"):
        gpu.save_array(vectors / f"model{suffix}.npy", np.ones((1, 2), dtype=np.float32))
    assert not gpu.vectors_complete(tmp_path, "model")
    for suffix in ("", "-queries", "-eval-queries"):
        (vectors / f"model{suffix}.index.json").write_text('{}')
    assert gpu.vectors_complete(tmp_path, "model")
    assert not list(vectors.glob("*.tmp"))


def test_encoding_retries_oom_without_truncating_or_reordering(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    class OutOfMemoryError(RuntimeError):
        pass

    monkeypatch.setitem(sys.modules, "torch", SimpleNamespace(
        cuda=SimpleNamespace(OutOfMemoryError=OutOfMemoryError)
    ))
    monkeypatch.setattr(gpu, "release_cuda", lambda: None)
    observed: list[list[str]] = []

    class Model:
        def encode(self, texts: list[str], **kwargs: Any) -> np.ndarray:
            if kwargs["batch_size"] > 2:
                raise OutOfMemoryError()
            observed.append(texts)
            return np.array([[int(text[-1]), 1] for text in texts], dtype=np.float32)

    vectors = gpu.encode(Model(), [str(i) for i in range(5)], "query: ", 4, label="check")
    assert vectors[:, 0].tolist() == [0, 1, 2, 3, 4]
    assert observed == [["query: 0", "query: 1"], ["query: 2", "query: 3"], ["query: 4"]]
    assert "check: 5/5" in capsys.readouterr().out


def test_train_uses_actual_seed_amp_and_resumable_checkpoints(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    captured: dict[str, Any] = {}
    seed = 3
    base = "BAAI/bge-small-en-v1.5"
    target = tmp_path / "checkpoints" / gpu.safe_id(base) / f"seed-{seed}"
    checkpoint = target / "checkpoints/checkpoint-50"
    checkpoint.mkdir(parents=True)
    # A partial model save is NOT a completion marker.
    (target / "config_sentence_transformers.json").write_text('{}')

    class Model:
        def save(self, path: str) -> None:
            assert Path(path) == target

    class Trainer:
        def __init__(self, **kwargs: Any) -> None:
            captured.update(kwargs)

        def train(self, **kwargs: Any) -> None:
            captured["train"] = kwargs

    monkeypatch.setitem(sys.modules, "torch", SimpleNamespace(
        manual_seed=lambda _: None, cuda=SimpleNamespace(manual_seed_all=lambda _: None)
    ))
    monkeypatch.setitem(sys.modules, "datasets", SimpleNamespace(
        Dataset=SimpleNamespace(from_dict=lambda value: value)
    ))
    monkeypatch.setitem(sys.modules, "sentence_transformers", SimpleNamespace(
        SentenceTransformerTrainer=Trainer,
        SentenceTransformerTrainingArguments=lambda **kwargs: kwargs,
    ))
    monkeypatch.setitem(sys.modules, "sentence_transformers.losses", SimpleNamespace(
        MultipleNegativesRankingLoss=lambda model: "MNRL",
    ))
    monkeypatch.setitem(sys.modules, "transformers.trainer_utils", SimpleNamespace(
        get_last_checkpoint=lambda _: str(checkpoint)
    ))
    monkeypatch.setattr(gpu, "load_gpu_model", lambda _: Model())
    monkeypatch.setattr(gpu, "release_cuda", lambda: None)
    examples = [{"question": "q", "positive_text": "p", "negative_text": "n"}]
    assert gpu.train_one(base, seed, examples, tmp_path) == target
    args = captured["args"]
    assert (args["seed"], args["data_seed"], args["fp16"], args["bf16"]) == (3, 3, True, False)
    assert args["save_steps"] == 50 and args["report_to"] == "none"
    assert args["per_device_train_batch_size"] == 16
    assert captured["loss"] == "MNRL"
    assert captured["train"] == {"resume_from_checkpoint": str(checkpoint)}
    assert captured["train_dataset"] == {
        "anchor": [gpu.QUERY_PREFIX + "q"], "positive": ["p"], "negative": ["n"]
    }
    assert (target / "training_complete.json").is_file()
    monkeypatch.setattr(gpu, "load_gpu_model", lambda _: pytest.fail("must reuse complete model"))
    assert gpu.train_one(base, seed, examples, tmp_path) == target
