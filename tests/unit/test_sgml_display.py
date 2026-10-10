from pathlib import Path

from rag_service.benchmark.corpus import _SgmlCollector, parse_postgresql_source


def test_real_parameter_and_command_xrefs_keep_legacy_identities(tmp_path: Path) -> None:
    text = '''<sect1 id="runtime-config-autovacuum"><title>Automatic Vacuuming</title>
      <para>Controls whether the server should run the autovacuum launcher daemon.
      This is on by default; however, <xref linkend="guc-track-counts"/> must also
      be enabled for autovacuum to work.</para>
      <para>It can be overridden for <xref linkend="sql-vacuum"/> and
      <xref linkend="sql-analyze"/> when passing the BUFFER_USAGE_LIMIT option.</para>
      </sect1><varlistentry id="guc-track-counts" xreflabel="track_counts"/>
      <refentry id="sql-vacuum"><refmeta><refentrytitle>VACUUM</refentrytitle></refmeta></refentry>
      <refentry id="sql-analyze"><refmeta><refentrytitle>ANALYZE</refentrytitle>
      </refmeta></refentry>'''
    (tmp_path / "config.sgml").write_text(text)
    old = _SgmlCollector("pg-16", "config.sgml")
    old.feed(text)
    old.close()
    parsed = parse_postgresql_source(tmp_path, "pg-16")
    result = next(r for r in parsed if r.section_id == "runtime-config-autovacuum")
    assert "track_counts must also be enabled" in result.text
    assert "overridden for VACUUM and ANALYZE" in result.text
    assert {(r.section_id, r.lineage_key) for r in parsed} == {
        (r.section_id, r.lineage_key) for r in old.nodes}


def test_real_catalog_caption_does_not_overwrite_parent_or_generated_id(tmp_path: Path) -> None:
    text = '''<sect1 id="catalog-pg-subscription">
      <title><structname>pg_subscription</structname></title>
      <para>The catalog contains all existing logical replication subscriptions.</para>
      <table id="pg-subscription"><title><structname>pg_subscription</structname> Columns</title>
      <tgroup><tbody><row><entry><structfield>substream</structfield> <type>char</type></entry>
      </row></tbody></tgroup></table><sect2><title>Details</title><para>More information.</para>
      </sect2></sect1>'''
    (tmp_path / "catalogs.sgml").write_text(text)
    old = _SgmlCollector("pg-16", "catalogs.sgml")
    old.feed(text)
    old.close()
    parsed = parse_postgresql_source(tmp_path, "pg-16")
    assert {(r.section_id, r.lineage_key) for r in parsed} == {
        (r.section_id, r.lineage_key) for r in old.nodes}
    table = next(r for r in parsed if r.kind == "table")
    assert table.caption == "pg_subscription Columns"
    assert table.title == "pg_subscription"
    child = next(r for r in parsed if r.title == "Details")
    assert child.section_path == ("pg_subscription", "Details")


def test_reference_only_new_sections_are_excluded_without_shifting_siblings(tmp_path: Path) -> None:
    text = '''<chapter id="jit"><title>Just-in-Time Compilation</title>
      <para>General description.</para>
      <sect1 id="references"><title>See Also</title><xref linkend="jit"/></sect1>
      <sect1><title>When to JIT?</title><para>JIT compilation is beneficial primarily
      for long-running CPU-bound queries.</para></sect1></chapter>'''
    (tmp_path / "jit.sgml").write_text(text)
    old = _SgmlCollector("pg-17", "jit.sgml")
    old.feed(text)
    old.close()
    impact: dict[str, object] = {}
    parsed = parse_postgresql_source(tmp_path, "pg-17", impact=impact)
    assert {(r.section_id, r.lineage_key) for r in parsed} == {
        (r.section_id, r.lineage_key) for r in old.nodes}
    added = impact["new_records"]
    assert isinstance(added, list) and len(added) == 1
    assert added[0]["characters"] == 33 and added[0]["source_line"] == 3
    assert added[0]["reference_only"] is True and added[0]["excluded"] is True
    assert added[0]["lineage_key"].startswith("pg-section:xref-restored-")
