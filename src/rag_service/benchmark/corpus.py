"""Parse the official PostgreSQL documentation source into inspectable records.

PostgreSQL publishes its documentation in the source archive under ``doc/src/sgml``.
The parser intentionally understands only the structural SGML used by the manuals;
it does not attempt to render HTML and therefore remains deterministic and offline
after the source archive has been downloaded.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict, dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

_SECTION_TAGS = {
    "appendix",
    "chapter",
    "part",
    "refentry",
    "refsect1",
    "refsect2",
    "refsect3",
    "sect1",
    "sect2",
    "sect3",
    "sect4",
    "sect5",
}
_CODE_TAGS = {"programlisting", "screen", "literallayout", "synopsis"}
_TABLE_TAGS = {"table", "informaltable"}
_IGNORED_TAGS = {"indexterm", "anchor"}
_WS_RE = re.compile(r"\s+")


@dataclass(frozen=True, slots=True)
class SourceRecord:
    """One evidence-bearing structural block from one manual version."""

    version: str
    lineage_key: str
    section_id: str
    section_path: tuple[str, ...]
    title: str
    text: str
    kind: str
    source_file: str
    source_line: int
    table_rows: tuple[tuple[str, ...], ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)
    caption: str = ""

    def to_json(self) -> dict[str, Any]:
        value = asdict(self)
        value["section_path"] = list(self.section_path)
        value["table_rows"] = [list(row) for row in self.table_rows]
        return value

    @classmethod
    def from_json(cls, value: dict[str, Any]) -> SourceRecord:
        return cls(
            version=str(value["version"]),
            lineage_key=str(value["lineage_key"]),
            section_id=str(value["section_id"]),
            section_path=tuple(str(item) for item in value.get("section_path", [])),
            title=str(value.get("title", "")),
            text=str(value["text"]),
            kind=str(value.get("kind", "text")),
            source_file=str(value.get("source_file", "")),
            source_line=int(value.get("source_line", 1)),
            table_rows=tuple(
                tuple(str(cell) for cell in row) for row in value.get("table_rows", [])
            ),
            metadata=dict(value.get("metadata", {})),
            caption=str(value.get("caption", "")),
        )


@dataclass(slots=True)
class _Node:
    tag: str
    section_id: str
    title: str
    path: tuple[str, ...]
    source_file: str
    source_line: int
    prose: list[str] = field(default_factory=list)
    blocks: list[tuple[str, str, tuple[tuple[str, ...], ...]]] = field(default_factory=list)
    title_depth: int = 0
    title_parts: list[str] = field(default_factory=list)
    ignored_depth: int = 0


class _SgmlCollector(HTMLParser):
    """Collect direct text, code blocks, and table rows for structural nodes."""

    def __init__(self, version: str, source_file: str) -> None:
        super().__init__(convert_charrefs=True)
        self.version = version
        self.source_file = source_file
        self.nodes: list[SourceRecord] = []
        self._stack: list[_Node] = []
        self._capture: str | None = None
        self._capture_parts: list[str] = []
        self._table_rows: list[list[str]] = []
        self._table_row: list[str] | None = None
        self._table_cell: list[str] | None = None
        self._table_header = False
        self._table_depth = 0
        self._capture_node: _Node | None = None
        self._ignored = 0
        self._lineage_fallbacks: dict[str, int] = {}

    @property
    def _current(self) -> _Node | None:
        return self._stack[-1] if self._stack else None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        if tag in _IGNORED_TAGS:
            self._ignored += 1
            return
        if self._ignored:
            return
        attributes = dict(attrs)
        if tag in _SECTION_TAGS:
            section_id = attributes.get("id") or attributes.get("xml:id") or ""
            if not section_id:
                parent = "/".join(self._current.path if self._current else ())
                seed = f"{self.source_file}:{parent}:{len(self.nodes)}"
                section_id = "generated-" + hashlib.sha256(seed.encode()).hexdigest()[:16]
            parent_path = self._current.path if self._current else ()
            title = section_id
            self._stack.append(
                _Node(
                    tag=tag,
                    section_id=section_id,
                    title=title,
                    path=parent_path + (title,),
                    source_file=self.source_file,
                    source_line=self.getpos()[0],
                )
            )
            return
        current = self._current
        if current is None:
            return
        if tag == "title":
            current.title_depth += 1
            current.title_parts.clear()
        elif tag in _CODE_TAGS and self._capture is None:
            self._capture = "code"
            self._capture_parts = []
            self._capture_node = current
        elif tag in _TABLE_TAGS and self._capture is None:
            self._capture = "table"
            self._capture_parts = []
            self._capture_node = current
            self._table_rows = []
            self._table_row = None
            self._table_cell = None
            self._table_depth = 1
        elif self._capture == "table":
            if tag in _TABLE_TAGS:
                self._table_depth += 1
            elif tag in {"tr", "row"}:
                self._table_row = []
                self._table_header = False
            elif tag in {"td", "th", "entry"}:
                self._table_cell = []
                self._table_header = self._table_header or tag == "th"

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in _IGNORED_TAGS:
            self._ignored = max(0, self._ignored - 1)
            return
        if self._ignored:
            return
        current = self._current
        if current is None:
            return
        if tag == "title" and current.title_depth:
            current.title_depth -= 1
            if current.title_depth == 0:
                title = _clean("".join(current.title_parts))
                if title:
                    old_path = current.path
                    current.title = title
                    current.path = old_path[:-1] + (title,)
                    if len(self._stack) > 1:
                        for node in self._stack[:-1]:
                            if node.path and node.path[-1] == old_path[-1]:
                                node.path = node.path[:-1] + (node.title,)
            return
        if self._capture == "table" and current is self._capture_node:
            if tag in {"td", "th", "entry"} and self._table_cell is not None:
                self._table_row = self._table_row or []
                self._table_row.append(_clean("".join(self._table_cell)))
                self._table_cell = None
            elif tag in {"tr", "row"} and self._table_row:
                self._table_rows.append(self._table_row)
                self._table_row = None
            elif tag in _TABLE_TAGS:
                self._table_depth -= 1
                if self._table_depth == 0:
                    rows = tuple(tuple(row) for row in self._table_rows if row)
                    text = _rows_to_text(rows)
                    if text and any(cell.strip() for row in rows for cell in row):
                        current.blocks.append(("table", text, rows))
                    self._capture = None
                    self._capture_node = None
                    self._table_rows = []
            return
        if self._capture == "code" and current is self._capture_node and tag in _CODE_TAGS:
            text = "".join(self._capture_parts).strip()
            if text:
                current.blocks.append(("code", text, ()))
            self._capture = None
            self._capture_node = None
            self._capture_parts = []
            return
        if tag in _SECTION_TAGS and current is not None and current.tag == tag:
            self._finish_node()

    def handle_data(self, data: str) -> None:
        if self._ignored:
            return
        current = self._current
        if current is None:
            return
        if current.title_depth:
            current.title_parts.append(data)
        elif self._capture == "table" and self._table_cell is not None:
            self._table_cell.append(data)
        elif self._capture == "code":
            self._capture_parts.append(data)
        elif data.strip():
            current.prose.append(data)

    def close(self) -> None:
        super().close()
        while self._stack:
            self._finish_node()

    def _finish_node(self) -> None:
        node = self._stack.pop()
        title = _clean(node.title)
        prose = _clean(" ".join(node.prose))
        lineage = _stable_lineage(node.section_id)
        if prose:
            text = f"{title}\n{prose}" if title and title != node.section_id else prose
            self.nodes.append(
                SourceRecord(
                    version=self.version,
                    lineage_key=lineage,
                    section_id=node.section_id,
                    section_path=node.path,
                    title=title,
                    text=text,
                    kind="text",
                    source_file=node.source_file,
                    source_line=node.source_line,
                )
            )
        for index, (kind, text, rows) in enumerate(node.blocks):
            self.nodes.append(
                SourceRecord(
                    version=self.version,
                    lineage_key=f"{lineage}#{kind}{index}",
                    section_id=node.section_id,
                    section_path=node.path,
                    title=title,
                    text=text,
                    kind=kind,
                    source_file=node.source_file,
                    source_line=node.source_line,
                    table_rows=rows,
                    metadata={"section_lineage": lineage},
                )
            )


def _stable_lineage(section_id: str) -> str:
    return "pg-section:" + section_id


def _clean(value: str) -> str:
    return _WS_RE.sub(" ", value).strip()


def _rows_to_text(rows: tuple[tuple[str, ...], ...]) -> str:
    if not rows:
        return ""
    width = max(len(row) for row in rows)
    normalized = [row + ("",) * (width - len(row)) for row in rows]
    lines = ["| " + " | ".join(row) + " |" for row in normalized]
    if len(lines) > 1:
        lines.insert(1, "| " + " | ".join("---" for _ in range(width)) + " |")
    return "\n".join(lines)


def parse_postgresql_source(
    source_dir: str | Path, version: str, *, impact: dict[str, Any] | None = None,
) -> list[SourceRecord]:
    """Parse all SGML files in one extracted PostgreSQL source tree."""

    root = Path(source_dir)
    if (root / "doc" / "src" / "sgml").is_dir():
        root = root / "doc" / "src" / "sgml"
    if not root.is_dir():
        raise FileNotFoundError(f"PostgreSQL SGML directory not found: {root}")
    # The legacy collector remains the identity authority. Rendering changes
    # cannot change its path/record-count-dependent fallback IDs.
    from .sgml_display import parse_preserving_identities

    records = parse_preserving_identities(root, version, impact=impact)
    records.sort(key=lambda item: (item.source_file, item.source_line, item.kind, item.text))
    return records


def write_source_records(records: list[SourceRecord], path: str | Path) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record.to_json(), ensure_ascii=False, sort_keys=True) + "\n")


def load_source_records(path: str | Path) -> list[SourceRecord]:
    records: list[SourceRecord] = []
    with Path(path).open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                records.append(SourceRecord.from_json(json.loads(line)))
    return records


__all__ = ["SourceRecord", "load_source_records", "parse_postgresql_source", "write_source_records"]
