"""Small source adapters for the first ingestion vertical slice."""

from __future__ import annotations

from collections.abc import Iterable
from html.parser import HTMLParser
from pathlib import Path

from rag_service.domain import DocumentSection, SourceLocation


class LocalTextParser:
    """Read a UTF-8 text or Markdown file without changing its structure."""

    def parse(self, source: SourceLocation) -> Iterable[DocumentSection]:
        if not source.path:
            raise ValueError("LocalTextParser requires SourceLocation.path")
        path = Path(source.path)
        text = path.read_text(encoding="utf-8")
        yield DocumentSection(
            text=text,
            page_number=source.page_number,
            page_metadata={"file_name": path.name, "file_type": path.suffix.lower()},
            source=source,
        )


class PyMuPDFParser:
    """Extract one structural section per PDF page.

    PyMuPDF is optional so the API can still run in a minimal environment. This
    path extracts embedded PDF text only; it does not perform OCR or promise
    reliable table extraction.
    """

    def parse(self, source: SourceLocation) -> Iterable[DocumentSection]:
        if not source.path:
            raise ValueError("PyMuPDFParser requires SourceLocation.path")
        try:
            import fitz
        except ImportError as exc:
            raise RuntimeError(
                "PDF ingestion requires the optional 'documents' dependency: pymupdf"
            ) from exc

        path = Path(source.path)
        with fitz.open(path) as document:
            for page_index, page in enumerate(document, start=1):
                text = page.get_text("text").strip()
                if not text:
                    continue
                yield DocumentSection(
                    text=text,
                    page_number=page_index,
                    page_metadata={
                        "file_name": path.name,
                        "file_type": ".pdf",
                        "page_index": page_index - 1,
                    },
                    source=SourceLocation(
                        uri=source.uri,
                        path=source.path,
                        page_number=page_index,
                        fragment=source.fragment,
                        metadata=source.metadata,
                    ),
                )


class _HTMLSectionCollector(HTMLParser):
    """Collect headings and text without changing the parser dependency surface."""

    def __init__(self) -> None:
        super().__init__()
        self.sections: list[DocumentSection] = []
        self._heading: str | None = None
        self._level = 0
        self._parts: list[str] = []
        self._special_kind: str | None = None
        self._special_parts: list[str] = []
        self._table_rows: list[list[str]] = []
        self._table_row: list[str] | None = None
        self._table_cell: list[str] | None = None
        self._table_depth = 0
        self._ignored_table_depth = 0
        self._pre_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if self._special_kind == "table":
            if tag == "table":
                self._table_depth += 1
            elif tag == "tr":
                self._table_row = []
            elif tag in {"td", "th"}:
                self._table_cell = []
            return
        if self._special_kind == "ignored_table":
            if tag == "table":
                self._ignored_table_depth += 1
            return
        if self._special_kind == "code":
            if tag == "pre":
                self._pre_depth += 1
            return
        if tag == "table":
            summary = dict(attrs).get("summary", "") or ""
            self._flush()
            if summary.startswith("Navigation"):
                self._special_kind = "ignored_table"
                self._ignored_table_depth = 1
            else:
                self._special_kind = "table"
                self._table_depth = 1
                self._table_rows = []
            return
        if tag == "pre":
            self._flush()
            self._special_kind = "code"
            self._special_parts = []
            self._pre_depth = 1
            return
        if tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            self._flush()
            self._heading = None
            self._level = int(tag[1])
        elif tag in {"p", "pre", "li", "tr"}:
            self._parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if self._special_kind == "table":
            if tag in {"td", "th"} and self._table_cell is not None:
                self._table_row = self._table_row or []
                self._table_row.append(" ".join("".join(self._table_cell).split()))
                self._table_cell = None
            elif tag == "tr" and self._table_row:
                self._table_rows.append(self._table_row)
                self._table_row = None
            elif tag == "table":
                self._table_depth -= 1
                if self._table_depth == 0:
                    self._emit_table()
            return
        if self._special_kind == "ignored_table":
            if tag == "table":
                self._ignored_table_depth -= 1
                if self._ignored_table_depth == 0:
                    self._special_kind = None
            return
        if self._special_kind == "code":
            if tag == "pre":
                self._pre_depth -= 1
                if self._pre_depth == 0:
                    text = "".join(self._special_parts).strip()
                    if text:
                        self.sections.append(DocumentSection(text=text, kind="code"))
                    self._special_kind = None
                    self._special_parts.clear()
            return
        if tag in {"h1", "h2", "h3", "h4", "h5", "h6", "p", "pre", "li", "tr"}:
            self._flush_heading_or_text()

    def handle_data(self, data: str) -> None:
        if self._special_kind == "table":
            if self._table_cell is not None:
                self._table_cell.append(data)
            return
        if self._special_kind == "code":
            self._special_parts.append(data)
            return
        if self._special_kind == "ignored_table":
            return
        if data.strip():
            if self._level and self._heading is None:
                self._heading = data.strip()
            else:
                self._parts.append(data)

    def close(self) -> None:
        super().close()
        self._flush()

    def _flush_heading_or_text(self) -> None:
        if self._heading is not None:
            self.sections.append(
                DocumentSection(text=self._heading, heading=self._heading, level=self._level)
            )
            self._heading = None
            self._level = 0
            self._parts.clear()
        else:
            self._flush()

    def _flush(self) -> None:
        text = " ".join("".join(self._parts).split())
        if text:
            self.sections.append(DocumentSection(text=text))
        self._parts.clear()

    def _emit_table(self) -> None:
        rows = [row for row in self._table_rows if row]
        if rows:
            width = max(len(row) for row in rows)
            normalized = [row + [""] * (width - len(row)) for row in rows]
            markdown = [
                "| " + " | ".join(normalized[0]) + " |",
                "| " + " | ".join("---" for _ in range(width)) + " |",
            ]
            markdown.extend("| " + " | ".join(row) + " |" for row in normalized[1:])
            self.sections.append(DocumentSection(text="\n".join(markdown), kind="table"))
        self._special_kind = None
        self._table_rows.clear()
        self._table_row = None
        self._table_cell = None


class MarkdownHtmlParser(LocalTextParser):
    """Prefer UTF-8 Markdown/HTML; preserve a simple structural HTML output."""

    def parse(self, source: SourceLocation) -> Iterable[DocumentSection]:
        if not source.path:
            raise ValueError("MarkdownHtmlParser requires SourceLocation.path")
        path = Path(source.path)
        if path.suffix.lower() not in {".html", ".htm"}:
            yield from super().parse(source)
            return
        collector = _HTMLSectionCollector()
        collector.feed(path.read_text(encoding="utf-8"))
        collector.close()
        for section in collector.sections:
            yield DocumentSection(
                text=section.text,
                heading=section.heading,
                level=section.level,
                page_metadata={"file_name": path.name, "file_type": path.suffix.lower()},
                source=source,
                kind=section.kind,
            )


__all__ = ["LocalTextParser", "MarkdownHtmlParser", "PyMuPDFParser"]
