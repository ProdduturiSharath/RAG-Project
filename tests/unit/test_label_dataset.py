import argparse
import json
import runpy
from pathlib import Path
from typing import Any

from rag_service.benchmark.corpus import SourceRecord, write_source_records
from rag_service.benchmark.validation import is_final_gold


def test_review_acceptance_and_rejection_flags(tmp_path: Path, monkeypatch: Any) -> None:
    tool = runpy.run_path("scripts/label_dataset.py")
    candidates = tmp_path / "candidates.jsonl"
    output = tmp_path / "reviewed.jsonl"
    candidates.write_text("\n".join(json.dumps({"id": key, "question": "Example?"})
                                     for key in ("reject", "accept")) + "\n")
    answers = iter(["r", "a"])
    monkeypatch.setattr("builtins.input", lambda _: next(answers))
    tool["review"](argparse.Namespace(candidates=candidates, output=output))
    rejected, accepted = [json.loads(line) for line in output.read_text().splitlines()]
    assert rejected["review_status"] == "rejected" and rejected["validated"] is False
    assert accepted["review_status"] == "accepted" and accepted["validated"] is True
    assert not is_final_gold(rejected) and is_final_gold(accepted)
    assert not is_final_gold({**rejected, "validated": True})  # Legacy rejected row.
    assert not is_final_gold({"validated": True})  # No explicit acceptance.
    assert not is_final_gold({"validated": False, "review_status": "accepted"})


def test_future_blind_rows_have_explicit_acceptance(tmp_path: Path, monkeypatch: Any) -> None:
    tool = runpy.run_path("scripts/label_dataset.py")
    source = tmp_path / "source.jsonl"
    splits = tmp_path / "splits.json"
    output = tmp_path / "blind.jsonl"
    # Synthetic fixture, never a private blind question file.
    write_source_records([SourceRecord("pg-17", "synthetic", "synthetic", ("Synthetic",),
                                        "Synthetic", "The answer is four.", "text", "fake", 1)],
                         source)
    splits.write_text(json.dumps({"assignments": {"synthetic": "blind"}}))
    answers = iter(["What is the synthetic value?", "four", "The answer is four."])
    monkeypatch.setattr("builtins.input", lambda _: next(answers))
    tool["write_blind"](argparse.Namespace(source=source, splits=splits, output=output))
    row = json.loads(output.read_text())
    assert row["review_status"] == "accepted" and is_final_gold(row)
