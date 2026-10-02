"""Small source adapters for the first ingestion vertical slice."""

from __future__ import annotations

from collections.abc import Iterable
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

    PyMuPDF is optional so the API can still run in a minimal environment.  A
    later parser can add OCR and table extraction while keeping this output
    contract unchanged.
    """

    def parse(self, source: SourceLocation) -> Iterable[DocumentSection]:
        if not source.path:
            raise ValueError("PyMuPDFParser requires SourceLocation.path")
        try:
            import fitz  # type: ignore[import-not-found]
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


__all__ = ["LocalTextParser", "PyMuPDFParser"]
