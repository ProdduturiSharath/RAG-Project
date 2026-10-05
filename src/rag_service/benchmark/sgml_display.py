"""Plain SGML reference/caption rendering with frozen legacy record identities."""

from __future__ import annotations

import hashlib
from collections import Counter
from dataclasses import replace
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

from .corpus import SourceRecord, _SgmlCollector


class _PlainInline(HTMLParser):
    def __init__(self, labels: dict[str, str]) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.labels = labels

    def handle_data(self, value: str) -> None:
        self.parts.append(value)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "xref":
            label = self.labels.get(str(dict(attrs).get("linkend", "")))
            if label:
                self.parts.append(label)


def _plain(text: str, labels: dict[str, str]) -> str:
    collector = _PlainInline(labels)
    collector.feed(text)
    collector.close()
    return " ".join("".join(collector.parts).split())


class _ReferenceIndex(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.labels: dict[str, str] = {}
        self.frames: list[tuple[str, str]] = []
        self.capture = ""
        self.parts: list[str] = []
        self.targets: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        key = str(attributes.get("id") or attributes.get("xml:id") or "")
        self.frames.append((tag, key))
        if key and attributes.get("xreflabel"):
            self.labels[key] = _plain(str(attributes["xreflabel"]), {})
        if tag in {"title", "refentrytitle", "refname"} and not self.capture:
            self.capture, self.parts = tag, []
            self.targets = [value for _, value in self.frames if value and value not in self.labels]

    def handle_data(self, value: str) -> None:
        if self.capture:
            self.parts.append(value)

    def handle_endtag(self, tag: str) -> None:
        if tag == self.capture:
            value = _plain("".join(self.parts), self.labels)
            if value:
                for key in self.targets:
                    self.labels.setdefault(key, value)
            self.capture = ""
        for index in range(len(self.frames) - 1, -1, -1):
            if self.frames[index][0] == tag:
                del self.frames[index:]
                break


class _LegacyIdentityCollector(_SgmlCollector):
    def __init__(self, version: str, source_file: str) -> None:
        super().__init__(version, source_file)
        self.section_identities: dict[int, str] = {}

    def _finish_node(self) -> None:
        node = self._stack[-1]
        self.section_identities[node.source_line] = node.section_id
        super()._finish_node()


class _DisplayCollector(_SgmlCollector):
    def __init__(self, version: str, source_file: str, labels: dict[str, str]) -> None:
        super().__init__(version, source_file)
        self.labels = labels
        self.caption_parts: list[str] | None = None
        self.caption = ""
        self.captions: dict[tuple[int, int], str] = {}
        self.links: list[tuple[str, bool]] = []
        self.unresolved: Counter[str] = Counter()
        self.literal_prose: set[int] = set()
        self.reference_only: set[int] = set()
        self.injecting_reference = False

    def _reference(self, label: str) -> None:
        self.injecting_reference = True
        self.handle_data(label)
        self.injecting_reference = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if not self._ignored and tag == "title" and self._capture == "table":
            self.caption_parts = []
            return
        if not self._ignored and tag == "xref" and self._current and self._capture != "code":
            target = str(attributes.get("linkend", ""))
            label = self.labels.get(target)
            if label:
                self._reference(label)
            else:
                self.unresolved[target] += 1
            return
        if not self._ignored and tag == "link" and self._capture != "code":
            self.links.append((str(attributes.get("linkend", "")), False))
        if tag in {"table", "informaltable"} and self._capture is None:
            self.caption = ""
        super().handle_starttag(tag, attrs)

    def handle_data(self, value: str) -> None:
        if self.links and value.strip():
            self.links[-1] = (self.links[-1][0], True)
        if (self._current and not self._ignored and not self._current.title_depth
                and self._capture is None and not self.injecting_reference
                and any(char.isalnum() for char in value)):
            self.literal_prose.add(self._current.source_line)
        if self.caption_parts is not None:
            self.caption_parts.append(value)
        else:
            super().handle_data(value)

    def handle_endtag(self, tag: str) -> None:
        if tag == "title" and self.caption_parts is not None:
            self.caption = _plain("".join(self.caption_parts), self.labels)
            self.caption_parts = None
            return
        if tag == "link" and self.links:
            target, has_text = self.links.pop()
            if not has_text and target in self.labels:
                self._reference(self.labels[target])
        if (tag in {"table", "informaltable"} and self._capture == "table"
                and self._table_depth == 1 and self._capture_node):
            self.captions[self._capture_node.source_line,
                          len(self._capture_node.blocks)] = self.caption
        current = self._current
        is_section_title = tag == "title" and current is not None and current.title_depth > 0
        super().handle_endtag(tag)
        if is_section_title and current and current.title_depth == 0:
            current.title = _plain(current.title, self.labels)
            current.path = current.path[:-1] + (current.title,)

    def _finish_node(self) -> None:
        node = self._stack[-1]
        if node.source_line not in self.literal_prose:
            self.reference_only.add(node.source_line)
        start = len(self.nodes)
        super()._finish_node()
        for index in range(start, len(self.nodes)):
            record = self.nodes[index]
            if record.kind == "table":
                block_index = int(record.lineage_key.rsplit("table", 1)[1])
                caption = self.captions.get((record.source_line, block_index), "")
                self.nodes[index] = replace(record, caption=caption,
                                            metadata={**record.metadata, "table_caption": caption})


def _slots(records: list[SourceRecord]) -> dict[tuple[int, str, int], SourceRecord]:
    occurrence: Counter[tuple[int, str]] = Counter()
    result = {}
    for record in records:
        key = record.source_line, record.kind
        result[*key, occurrence[key]] = record
        occurrence[key] += 1
    return result


def parse_preserving_identities(
    root: Path, version: str, *, impact: dict[str, Any] | None = None,
) -> list[SourceRecord]:
    texts = [(path, path.read_text(encoding="utf-8", errors="replace"))
             for path in sorted(root.rglob("*.sgml"))]
    index = _ReferenceIndex()
    for _, text in texts:
        index.feed(text)
        index.close()
        index.frames.clear()
    records = []
    additions = []
    unresolved: Counter[str] = Counter()
    for path, text in texts:
        source_file = path.relative_to(root).as_posix()
        legacy = _LegacyIdentityCollector(version, source_file)
        display = _DisplayCollector(version, source_file, index.labels)
        for collector in (legacy, display):
            collector.feed(text)
            collector.close()
        before, after = _slots(legacy.nodes), _slots(display.nodes)
        if not before.keys() <= after.keys():
            raise ValueError(f"display repair removed existing records in {source_file}")
        family_by_line = {r.source_line: "pg-section:" + r.section_id for r in legacy.nodes}
        for slot, record in after.items():
            prior = before.get(slot)
            if prior:
                metadata = {**record.metadata, "legacy_heading_path": list(prior.section_path)}
                if prior.metadata.get("section_lineage"):
                    metadata["section_lineage"] = prior.metadata["section_lineage"]
                records.append(replace(record, section_id=prior.section_id,
                                       lineage_key=prior.lineage_key, metadata=metadata))
            else:
                ref_only = record.source_line in display.reference_only
                excluded = len(record.text) < 50 or ref_only
                legacy_id = legacy.section_identities[record.source_line]
                logical_file = source_file.split("doc/src/sgml/")[-1]
                new_id = "xref-restored-" + hashlib.sha256(
                    f"{logical_file}:{legacy_id}".encode()).hexdigest()[:24]
                family = family_by_line.get(record.source_line)
                section_id = family.removeprefix("pg-section:") if family else new_id
                additions.append({"version": version, "source_file": source_file,
                                  "source_line": record.source_line, "characters": len(record.text),
                                  "reference_only": ref_only, "excluded": excluded,
                                  "section_id": section_id, "lineage_key": "pg-section:" + new_id,
                                  "family_key": family or "pg-section:" + new_id})
                if excluded:
                    continue
                records.append(replace(record, section_id=section_id,
                                       lineage_key="pg-section:" + new_id,
                                       metadata={**record.metadata, "section_lineage":
                                                 family or "pg-section:" + new_id,
                                                 "restored_reference_record": True}))
        unresolved.update(display.unresolved)
    if impact is not None:
        impact.update(new_records=additions, unresolved_references=dict(unresolved))
    identities = {(r.lineage_key, r.source_file, r.source_line, r.kind) for r in records}
    if len(identities) != len(records):
        raise ValueError("record identity collision")
    return records
