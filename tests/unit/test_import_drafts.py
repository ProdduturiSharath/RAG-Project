from typing import Any

import pytest

from rag_service.benchmark.corpus import SourceRecord
from rag_service.benchmark.drafts import DraftImporter


def source(lineage: str = "setting", text: str = "The default\n  is 4MB.") -> SourceRecord:
    return SourceRecord("pg-15", lineage, lineage, ("Settings",), "Settings", text,
                        "text", "config.sgml", 10)


def draft(**changes: Any) -> dict[str, Any]:
    return {"question": "What is the default memory allocation?", "type": "factoid",
            "expected_answer": "4MB", "lineage_key": "setting", "target_version": "pg-15",
            "evidence_quote": "The default is 4MB.", "paraphrased": True,
            "version_independent": True, **changes}


def test_whitespace_match_preserves_exact_source_offsets() -> None:
    importer = DraftImporter([source()], {"setting": "dev"})
    row = importer.accept(draft(validated=True), set())
    span = row["evidence_spans"][0]
    assert span["quote"] == "The default\n  is 4MB."
    assert source().text[span["start_char"]:span["end_char"]] == span["quote"]
    assert row["validated"] is False
    assert row["author"] == "llm_drafted"


@pytest.mark.parametrize("question", [
    "According to the passage, what is the default?",
    "What does this section say about memory allocation?",
    "What does the text say about memory?",
    "What does PostgreSQL documentation state?",
    "What is the default memory allocation? [variant 2]",
])
def test_rejects_meta_and_filler_questions(question: str) -> None:
    with pytest.raises(ValueError, match="passage/text/section|placeholder or vague"):
        DraftImporter([source()], {"setting": "dev"}).accept(draft(question=question), set())


def test_unanswerable_identifier_checks_entire_corpus_including_train() -> None:
    importer = DraftImporter([source(), source("hidden", "invented_cache_size")],
                             {"setting": "dev", "hidden": "train"})
    item = draft(question="What is the default for invented_cache_size?", type="unanswerable",
                 expected_answer="Not answerable", evidence_quote="",
                 invented_identifier="invented_cache_size")
    with pytest.raises(ValueError, match="occurs in corpus"):
        importer.accept(item, set())
    item.update(question="What is the default for quantum_cache_size?",
                invented_identifier="quantum_cache_size")
    row = importer.accept(item, set())
    assert row["evidence_spans"] == []
    assert row["answerability"] is False


@pytest.mark.parametrize("split", ["blind", "train"])
def test_rejects_forbidden_primary_and_evidence_lineages(split: str) -> None:
    importer = DraftImporter([source(), source("forbidden")],
                             {"setting": "dev", "forbidden": split})
    with pytest.raises(ValueError, match="primary lineage is not dev/test"):
        importer.accept(draft(lineage_key="forbidden"), set())
    with pytest.raises(ValueError, match="evidence lineage is not dev/test"):
        importer.accept(draft(evidence_spans=[{"lineage_key": "forbidden",
                                              "quote": "The default is 4MB."}]), set())


def test_batch_reports_duplicates_and_bad_quotes() -> None:
    importer = DraftImporter([source()], {"setting": "test"})
    rows, report = importer.import_batch([
        draft(), draft(), draft(question="How much memory can a sort allocate?",
                                evidence_quote="8MB")], [])
    assert len(rows) == 1
    assert report["discarded"] == 2
    assert {r["reason"] for r in report["reasons"]} == {
        "duplicate question", "quote absent from full source"}
