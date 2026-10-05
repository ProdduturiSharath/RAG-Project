import json
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory

from rag_service.benchmark.corpus import SourceRecord, parse_postgresql_source, write_source_records
from rag_service.benchmark.dataset import build_split_assignments
from rag_service.benchmark.diffs import build_diffs
from rag_service.benchmark.families import (
    family_map,
    manifest_errors,
    refresh_manifest,
    resolve_migration,
)
from rag_service.benchmark.validation import validate_dataset


def record(version: str, lineage: str, text: str, *, kind: str = "text") -> SourceRecord:
    return SourceRecord(
        version=version,
        lineage_key=lineage,
        section_id=lineage,
        section_path=("Configuration",),
        title="Configuration",
        text=text,
        kind=kind,
        source_file="postgresql.sgml",
        source_line=10,
    )


def test_lineage_split_assignment_is_deterministic_and_single_valued() -> None:
    records = [record("pg-15", "lineage-a", "old"), record("pg-16", "lineage-a", "new")]
    first = build_split_assignments(records)
    assert first == build_split_assignments(list(reversed(records)))
    assert set(first) == {"lineage-a"}
    assert len(set(first.values())) == 1


def test_lineage_refresh_preserves_assignments_and_blind_pool() -> None:
    previous = {"lineage-a": "test", "retired-blind": "blind", "retired": "dev"}
    records = [record("pg-15", "lineage-a", "changed"), record("pg-17", "new", "new")]
    result = build_split_assignments(records, previous)
    assert result == build_split_assignments(list(reversed(records)), previous)
    assert result["lineage-a"] == "test"
    assert {k for k, v in result.items() if v == "blind"} == {"retired-blind"}
    assert result["new"] in {"train", "dev", "test"}
    assert "retired" not in result


def test_block_only_family_and_new_versions_inherit_one_split() -> None:
    table = replace(record("pg-15", "pg-section:only#table0", "table", kind="table"),
                    section_id="only", metadata={"section_lineage": "pg-section:only"})
    code = replace(table, version="pg-17", lineage_key="pg-section:only#code1", kind="code")
    mapping = family_map([table, code])
    assert len(set(mapping.values())) == 1
    result = build_split_assignments([code, table], {table.lineage_key: "blind"},
                                     lineage_families=mapping)
    assert result == {table.lineage_key: "blind", code.lineage_key: "blind"}


def test_migration_resolves_transitive_conflicts_and_preserves_unexposed_blind() -> None:
    previous = {"a": "test", "a#table0": "blind", "b": "test", "c": "dev",
                "d#code0": "blind", "d#table1": "train"}
    mapping = {key: key.split("#")[0] for key in previous}
    result, _ = resolve_migration(previous, mapping, {"a": {"test"}, "c": {"dev"}},
                                  {"a", "b", "c"}, [{"a", "b"}, {"b", "c"}])
    assert result == {"a": "dev", "a#table0": "dev", "b": "dev", "c": "dev",
                      "d#code0": "blind", "d#table1": "blind"}


def test_manifest_checks_uncommitted_corpus_members_not_just_compact_evidence() -> None:
    prose = replace(record("pg-15", "pg-section:config", "text"), section_id="config")
    table = replace(prose, lineage_key="pg-section:config#table0", kind="table",
                    metadata={"section_lineage": "pg-section:config"})
    assignments = {prose.lineage_key: "dev", table.lineage_key: "test"}
    manifest = refresh_manifest([prose, table], assignments,
                                {"lineages": {}, "components": [], "exposed_families": []}, "hash")
    errors = manifest_errors(manifest, assignments, [prose])
    assert any("section family spans splits" in error for error in errors)


def test_diff_miner_emits_both_sides_for_default_and_table_changes() -> None:
    rows = (
        ("parameter", "old"),
        ("value", "1"),
    )
    records = [
        record(
            "pg-15", "lineage-a",
            "work_mem default is 4MB\n| parameter | value |\n| --- | --- |\n| work_mem | 4MB |",
        ),
        record(
            "pg-16", "lineage-a",
            "work_mem default is 8MB\n| parameter | value |\n| --- | --- |\n| work_mem | 8MB |",
        ),
        SourceRecord(
            version="pg-15", lineage_key="lineage-table", section_id="table",
            section_path=("Configuration",), title="Configuration", text="| parameter | old |",
            kind="table", source_file="postgresql.sgml", source_line=10, table_rows=rows,
        ),
        SourceRecord(
            version="pg-16", lineage_key="lineage-table", section_id="table",
            section_path=("Configuration",), title="Configuration", text="| parameter | new |",
            kind="table", source_file="postgresql.sgml", source_line=10,
            table_rows=(("parameter", "new"), ("value", "2")),
        ),
    ]
    diffs, stats = build_diffs(records, ("pg-15", "pg-16"))
    assert stats["lineages_matched"] == 2
    assert len(diffs) == 2
    assert all(len(item["evidence"]) == 2 for item in diffs)
    assert any(change["kind"] == "changed_default" for change in diffs[0]["changes"])


def test_sgml_parser_preserves_code_and_table_evidence() -> None:
    with TemporaryDirectory() as directory:
        root = Path(directory) / "doc" / "src" / "sgml"
        root.mkdir(parents=True)
        (root / "manual.sgml").write_text(
            '<sect1 id="config"><title>Configuration</title><para>Use work_mem.</para>'
            '<programlisting>SET work_mem = \'8MB\';</programlisting>'
            '<table><tgroup><tbody><row><entry>name</entry><entry>value</entry></row>'
            '</tbody></tgroup></table></sect1>',
            encoding="utf-8",
        )
        parsed = parse_postgresql_source(Path(directory), "pg-15")
    assert {item.kind for item in parsed} == {"text", "code", "table"}
    assert any("work_mem" in item.text for item in parsed)
    assert any(item.table_rows for item in parsed if item.kind == "table")


def test_default_change_is_attached_to_setting_not_nearby_reference() -> None:
    common = (
        "vacuum_buffer_usage_limit ( integer ) Controls the buffer strategy. "
        "If it exceeds 1/8 of shared_buffers it is capped. The default value is "
    )
    diffs, _ = build_diffs([
        record("pg-16", "memory", common + "256 kB ."),
        record("pg-17", "memory", common + "2MB ."),
    ], ("pg-16", "pg-17"))
    defaults = [c for c in diffs[0]["changes"] if c["kind"] == "changed_default"]
    assert defaults == [{"kind": "changed_default", "name": "vacuum_buffer_usage_limit",
                         "before": "256", "after": "2MB"}]


def test_sgml_parser_preserves_real_postgresql_table_with_title() -> None:
    with TemporaryDirectory() as directory:
        root = Path(directory) / "doc" / "src" / "sgml"
        root.mkdir(parents=True)
        (root / "manual.sgml").write_text(
            '<sect1 id="config"><title>Configuration</title>'
            '<table id="settings"><title>Settings</title><tgroup cols="2">'
            '<thead><row><entry>Name</entry><entry>Value</entry></row></thead>'
            '<tbody><row><entry>work_mem</entry><entry>8MB</entry></row></tbody>'
            '</tgroup></table></sect1>',
            encoding="utf-8",
        )
        parsed = parse_postgresql_source(Path(directory), "pg-15")
    tables = [item for item in parsed if item.kind == "table"]
    assert len(tables) == 1
    assert tables[0].table_rows == (("Name", "Value"), ("work_mem", "8MB"))


def test_validator_rejects_lineage_list_overlap() -> None:
    with TemporaryDirectory() as directory:
        root = Path(directory)
        source = root / "source.jsonl"
        write_source_records([record("pg-15", "lineage-a", "Answer here.")], source)
        dataset = root / "dataset.jsonl"
        dataset.write_text(
            json.dumps({
                "id": "q1", "question": "What?", "type": "factoid",
                "expected_answer": "Answer here.",
                "evidence_spans": [{
                    "lineage_key": "lineage-a", "version": "pg-15", "quote": "Answer here."
                }],
                "target_version": "pg-15", "answerability": True, "requester": "user",
                "acl_allowance": True, "lineage_key": "lineage-a", "split": "dev",
                "author": "generated", "validated": False,
            }) + "\n",
            encoding="utf-8",
        )
        splits = root / "splits.json"
        splits.write_text(json.dumps({
            "assignments": {"lineage-a": "dev"},
            "splits": {"dev": ["lineage-a"], "test": ["lineage-a"]},
        }), encoding="utf-8")
        result = validate_dataset(dataset, source, splits, require_targets=False)
    assert not result["valid"]
    assert any("multiple persisted split lists" in error for error in result["errors"])
