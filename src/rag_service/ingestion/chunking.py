"""Deterministic, structure-aware text chunking.

The chunker works on parser output rather than calling a tokenizer service.
It uses whitespace-delimited tokens for predictable boundaries and keeps the
original text between token boundaries, including punctuation.  Section paths
and page metadata remain first-class fields on every resulting chunk.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, replace
from typing import Any, Literal

from rag_service.domain import AccessPolicy, Chunk, DocumentSection, SourceLocation

_TOKEN_RE = re.compile(r"\S+")
_HEADING_RE = re.compile(r"^\s{0,3}(#{1,6})\s+(.+?)\s*$")
_TABLE_SEPARATOR_RE = re.compile(r"^\s*\|?\s*:?-{3,}:?\s*(?:\|\s*:?-{3,}:?\s*)+\|?\s*$")


@dataclass(frozen=True, slots=True)
class ChunkingConfig:
    """Limits for :class:`DeterministicChunker`.

    Tokenization is intentionally modest: a token is a run of non-whitespace
    characters.  This makes the result independent of an external model and
    is sufficient for a stable first ingestion pass.
    """

    max_tokens: int = 200
    overlap_tokens: int = 20
    detect_markdown_headings: bool = True

    def __post_init__(self) -> None:
        if self.max_tokens < 1:
            raise ValueError("max_tokens must be at least 1")
        if self.overlap_tokens < 0:
            raise ValueError("overlap_tokens cannot be negative")
        if self.overlap_tokens >= self.max_tokens:
            raise ValueError("overlap_tokens must be smaller than max_tokens")


@dataclass(frozen=True, slots=True)
class _SectionRecord:
    section: DocumentSection
    path: tuple[str, ...]
    section_id: str
    occurrence: int
    parent_path: tuple[str, ...]
    lineage_key: str


def _json_value(value: Any) -> Any:
    """Convert common metadata values into deterministic JSON values."""

    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Mapping):
        return {
            str(key): _json_value(item)
            for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))
        }
    if isinstance(value, (list, tuple)):
        return [_json_value(item) for item in value]
    if isinstance(value, set):
        return sorted((_json_value(item) for item in value), key=repr)
    return str(value)


def _canonical_json(value: Any) -> str:
    return json.dumps(
        _json_value(value),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def stable_section_id(
    document_id: str,
    version: str,
    section_path: Sequence[str],
    occurrence: int = 0,
) -> str:
    """Return a stable opaque identifier for a structural section."""

    payload = _canonical_json(
        {
            "document_id": document_id,
            "version": version,
            "section_path": list(section_path),
            "occurrence": occurrence,
        }
    )
    return f"section-{hashlib.sha256(payload.encode('utf-8')).hexdigest()}"


def stable_lineage_key(
    document_id: str,
    section_path: Sequence[str],
    occurrence: int = 0,
) -> str:
    """Return a version-independent key for one logical section lineage."""

    payload = _canonical_json(
        {
            "document_id": document_id,
            "section_path": list(section_path),
            "occurrence": occurrence,
        }
    )
    return f"lineage-{hashlib.sha256(payload.encode('utf-8')).hexdigest()}"


def content_hash_for_chunk(text: str, kind: str = "text") -> str:
    """Hash reusable chunk content independently from document/version IDs."""

    payload = _canonical_json({"kind": kind, "text": text.replace("\r\n", "\n")})
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def stable_chunk_id(
    document_id: str,
    version: str,
    section_path: Sequence[str],
    chunk_index: int,
    text: str,
    *,
    section_id: str | None = None,
) -> str:
    """Return a deterministic ID for one chunk.

    The content digest is included so two chunks at the same ordinal cannot
    silently collide when a parser changes a section.  ``section_id`` lets
    callers distinguish repeated headings with identical paths.
    """

    payload = _canonical_json(
        {
            "document_id": document_id,
            "version": version,
            "section_path": list(section_path),
            "section_id": section_id,
            "chunk_index": chunk_index,
            "text": text,
        }
    )
    return f"chunk-{hashlib.sha256(payload.encode('utf-8')).hexdigest()}"


def content_hash_for_sections(sections: Iterable[DocumentSection | Mapping[str, Any]]) -> str:
    """Hash parser output in a stable, provider-independent way."""

    canonical: list[dict[str, Any]] = []
    for section in sections:
        parsed = _coerce_section(section)
        canonical.append(
            {
                "text": parsed.text.replace("\r\n", "\n").replace("\r", "\n"),
                "heading": parsed.heading,
                "level": parsed.level,
                "section_path": list(parsed.section_path),
                "page_number": parsed.page_number,
                "page_metadata": parsed.page_metadata,
                "metadata": parsed.metadata,
                "section_id": parsed.section_id,
                "parent_section_id": parsed.parent_section_id,
                "source": parsed.source.stable_uri if parsed.source else None,
                "kind": parsed.kind,
                "lineage_key": parsed.lineage_key,
            }
        )
    payload = _canonical_json(canonical)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _source_from_value(value: Any) -> SourceLocation | None:
    if value is None or isinstance(value, SourceLocation):
        return value
    if isinstance(value, Mapping):
        return SourceLocation(
            uri=str(value.get("uri", "")),
            path=value.get("path"),
            page_number=value.get("page_number", value.get("page")),
            line_start=value.get("line_start"),
            line_end=value.get("line_end"),
            fragment=value.get("fragment"),
            metadata=value.get("metadata", {}),
        )
    return SourceLocation(uri=str(value))


def _coerce_section(value: DocumentSection | Mapping[str, Any]) -> DocumentSection:
    """Accept the domain model as well as the dict shape common from parsers."""

    if isinstance(value, DocumentSection):
        return value
    if not isinstance(value, Mapping):
        raise TypeError("sections must contain DocumentSection values or mappings")

    known = {
        "text",
        "content",
        "body",
        "heading",
        "title",
        "level",
        "section_path",
        "path",
        "page_number",
        "page",
        "page_metadata",
        "metadata",
        "section_id",
        "parent_section_id",
        "source",
        "children",
        "lineage_key",
        "kind",
    }
    metadata = dict(value.get("metadata", {}))
    # Preserve parser-specific fields instead of throwing them away.
    metadata.update(
        {
            str(key): item
            for key, item in value.items()
            if key not in known and str(key) not in metadata
        }
    )
    path_value = value.get("section_path", value.get("path", ()))
    if isinstance(path_value, str):
        path = (path_value,)
    else:
        path = tuple(path_value or ())
    return DocumentSection(
        text=str(value.get("text", value.get("content", value.get("body", "")))),
        heading=value.get("heading", value.get("title")),
        level=int(value.get("level", 0) or 0),
        section_path=path,
        page_number=value.get("page_number", value.get("page")),
        page_metadata=value.get("page_metadata", {}),
        metadata=metadata,
        section_id=value.get("section_id"),
        parent_section_id=value.get("parent_section_id"),
        source=_source_from_value(value.get("source")),
        lineage_key=value.get("lineage_key"),
        kind=value.get("kind", "text"),
    )


def _split_markdown_section(section: DocumentSection) -> list[DocumentSection]:
    """Split a raw section containing ATX headings into structural sections."""

    if not section.text or not any(
        _HEADING_RE.match(line) for line in section.text.splitlines()
    ):
        return [section]

    lines = section.text.splitlines(keepends=True)
    pieces: list[DocumentSection] = []
    current_heading: str | None = None
    current_level = section.level
    current_lines: list[str] = []

    def emit() -> None:
        nonlocal current_lines
        body = "".join(current_lines).strip()
        if body or current_heading is not None:
            # A heading without body is retained as text so its structural
            # node is not lost from an otherwise empty page.
            text = body or (current_heading or "")
            pieces.append(
                DocumentSection(
                    text=text,
                    heading=current_heading,
                    level=current_level,
                    section_path=section.section_path,
                    page_number=section.page_number,
                    page_metadata=section.page_metadata,
                    metadata=section.metadata,
                    section_id=section.section_id,
                    parent_section_id=section.parent_section_id,
                    source=section.source,
                    lineage_key=section.lineage_key,
                    kind=section.kind,
                )
            )
        current_lines = []

    fence: str | None = None
    for line in lines:
        stripped = line.lstrip()
        if stripped.startswith(("```", "~~~")):
            marker = stripped[:3]
            fence = None if fence == marker else marker if fence is None else fence
            current_lines.append(line)
            continue
        match = _HEADING_RE.match(line.rstrip("\r\n")) if fence is None else None
        if match:
            emit()
            current_level = len(match.group(1))
            current_heading = match.group(2).strip()
        else:
            current_lines.append(line)
    emit()
    return pieces or [section]


def _token_windows(text: str, max_tokens: int, overlap_tokens: int) -> list[str]:
    matches = list(_TOKEN_RE.finditer(text))
    if not matches:
        return []

    windows: list[str] = []
    start = 0
    while start < len(matches):
        end = min(start + max_tokens, len(matches))
        window = text[matches[start].start() : matches[end - 1].end()].strip()
        if window:
            windows.append(window)
        if end >= len(matches):
            break
        next_start = end - overlap_tokens
        # ChunkingConfig prevents overlap == max_tokens, but this guard keeps
        # the helper safe if called directly or changed later.
        start = max(start + 1, next_start)
    return windows


class DeterministicChunker:
    """Split parsed sections while retaining structural and page context."""

    def __init__(
        self,
        max_tokens: int = 200,
        overlap_tokens: int = 20,
        *,
        config: ChunkingConfig | None = None,
    ) -> None:
        if config is not None and (max_tokens != 200 or overlap_tokens != 20):
            raise ValueError("pass either config or max_tokens/overlap_tokens, not both")
        self.config = config or ChunkingConfig(max_tokens, overlap_tokens)

    def prepare_sections(
        self,
        sections: Iterable[DocumentSection | Mapping[str, Any]] | str,
    ) -> list[DocumentSection]:
        """Coerce input and optionally discover Markdown headings."""

        if isinstance(sections, str):
            values: Iterable[DocumentSection | Mapping[str, Any]] = (
                DocumentSection(text=sections),
            )
        else:
            values = sections

        prepared: list[DocumentSection] = []
        for value in values:
            section = _coerce_section(value)
            if self.config.detect_markdown_headings and section.heading is None:
                prepared.extend(_split_markdown_section(section))
            else:
                prepared.append(section)
        return prepared

    def chunk(
        self,
        sections: Iterable[DocumentSection | Mapping[str, Any]] | str,
        document_id: str = "document",
        version: str = "v1",
        *,
        access_policy: AccessPolicy | None = None,
    ) -> tuple[Chunk, ...]:
        """Return deterministic chunks in source order.

        Every chunk from a nested section points to the first chunk of its
        nearest structural parent.  That parent chunk lists first-child IDs,
        giving callers a directly traversable parent/child relationship while
        avoiding synthetic chunks for empty sections.
        """

        if not document_id.strip():
            raise ValueError("document_id cannot be empty")
        if not version.strip():
            raise ValueError("version cannot be empty")

        prepared = self.prepare_sections(sections)
        if not prepared:
            return ()

        records: list[_SectionRecord] = []
        occurrences: dict[tuple[str, ...], int] = {}
        stack: list[tuple[int, str]] = []

        for section in prepared:
            path = self._resolve_path(section, stack)
            occurrence = occurrences.get(path, 0)
            occurrences[path] = occurrence + 1
            section_id = section.section_id or stable_section_id(
                document_id, version, path, occurrence
            )
            records.append(
                _SectionRecord(
                    section=section,
                    path=path,
                    section_id=section_id,
                    occurrence=occurrence,
                    parent_path=path[:-1],
                    lineage_key=section.lineage_key
                    or stable_lineage_key(document_id, path, occurrence),
                )
            )

        # First chunks are representatives used for structural links.
        chunks: list[Chunk] = []
        representatives: dict[str, str] = {}
        record_first_indices: dict[str, int] = {}
        local_indices: dict[str, int] = {}

        for record in records:
            text = record.section.text
            if not text.strip() and record.section.heading:
                text = record.section.heading
            windows = self._structured_windows(text, record.section.kind)
            if not windows:
                continue

            page_number = self._page_number(record.section)
            for local_index, (kind, window) in enumerate(windows):
                chunk_id = stable_chunk_id(
                    document_id,
                    version,
                    record.path,
                    local_index,
                    window,
                    section_id=record.section_id,
                )
                parent_id = self._parent_representative_id(
                    record, records, representatives
                )
                chunk = Chunk(
                    chunk_id=chunk_id,
                    document_id=document_id,
                    version=version,
                    text=window,
                    section_path=record.path,
                    ordinal=len(chunks),
                    parent_id=parent_id,
                    page_number=page_number,
                    page_metadata=record.section.page_metadata,
                    metadata=record.section.metadata,
                    source=record.section.source,
                    section_id=record.section_id,
                    access_policy=access_policy,
                    kind=kind,
                    content_hash=content_hash_for_chunk(window, kind),
                    lineage_key=record.lineage_key,
                    parent_text=text,
                )
                if local_index == 0:
                    representatives[record.section_id] = chunk_id
                    record_first_indices[record.section_id] = len(chunks)
                local_indices[record.section_id] = local_index
                chunks.append(chunk)

        if not chunks:
            return ()

        # Attach direct child representatives to each structural parent.  A
        # section may have no text; in that case its child links roll up to the
        # nearest represented ancestor.
        child_ids_by_parent: dict[str, list[str]] = {}
        for record in records:
            child_representative = representatives.get(record.section_id)
            if child_representative is None:
                continue
            parent_record = self._nearest_record_for_path(record.parent_path, records)
            if parent_record is None:
                continue
            parent_representative = representatives.get(parent_record.section_id)
            if parent_representative is None:
                continue
            child_ids_by_parent.setdefault(parent_representative, []).append(
                child_representative
            )

        for index, chunk in enumerate(chunks):
            child_ids = tuple(dict.fromkeys(child_ids_by_parent.get(chunk.chunk_id, ())))
            if child_ids:
                chunks[index] = replace(chunk, child_ids=child_ids)

        return tuple(chunks)

    def chunk_sections(
        self,
        sections: Iterable[DocumentSection | Mapping[str, Any]] | str,
        document_id: str = "document",
        version: str = "v1",
        *,
        access_policy: AccessPolicy | None = None,
    ) -> tuple[Chunk, ...]:
        """Descriptive alias for :meth:`chunk`."""

        return self.chunk(
            sections,
            document_id=document_id,
            version=version,
            access_policy=access_policy,
        )

    __call__ = chunk

    @staticmethod
    def _resolve_path(
        section: DocumentSection,
        stack: list[tuple[int, str]],
    ) -> tuple[str, ...]:
        if section.section_path:
            path = tuple(str(item) for item in section.section_path if str(item).strip())
            stack[:] = [(index + 1, item) for index, item in enumerate(path)]
            return path

        if section.heading:
            level = section.level or 1
            while stack and stack[-1][0] >= level:
                stack.pop()
            stack.append((level, section.heading.strip()))
            return tuple(item for _, item in stack)

        return tuple(item for _, item in stack)

    @staticmethod
    def _page_number(section: DocumentSection) -> int | None:
        if section.page_number is not None:
            return section.page_number
        if section.source and section.source.page_number is not None:
            return section.source.page_number
        for key in ("page_number", "page"):
            value = section.metadata.get(key)
            if isinstance(value, int) and value > 0:
                return value
        return None

    def _structured_windows(
        self, text: str, kind: Literal["text", "table", "code"]
    ) -> list[tuple[Literal["text", "table", "code"], str]]:
        """Window prose; preserve each table/caption and fenced block intact."""

        if kind != "text":
            return [(kind, text.strip())] if text.strip() else []
        lines = text.splitlines(keepends=True)
        output: list[tuple[Literal["text", "table", "code"], str]] = []
        prose: list[str] = []

        def flush() -> None:
            output.extend(("text", window) for window in _token_windows(
                "".join(prose), self.config.max_tokens, self.config.overlap_tokens
            ))
            prose.clear()

        i = 0
        while i < len(lines):
            stripped = lines[i].lstrip()
            if stripped.startswith(("```", "~~~")):
                flush()
                marker = stripped[:3]
                block = [lines[i]]
                i += 1
                while i < len(lines):
                    block.append(lines[i])
                    i += 1
                    if block[-1].lstrip().startswith(marker):
                        break
                output.append(("code", "".join(block).strip()))
            elif i + 1 < len(lines) and _TABLE_SEPARATOR_RE.match(lines[i + 1]):
                # Markdown captions conventionally precede the table. Preserve
                # the preceding paragraph with it (including a blank separator).
                caption: list[str] = []
                while prose and not prose[-1].strip():
                    caption.insert(0, prose.pop())
                while prose and prose[-1].strip():
                    caption.insert(0, prose.pop())
                flush()
                block = caption + [lines[i], lines[i + 1]]
                i += 2
                while i < len(lines) and "|" in lines[i] and lines[i].strip():
                    block.append(lines[i])
                    i += 1
                output.append(("table", "".join(block).strip()))
            else:
                prose.append(lines[i])
                i += 1
        flush()
        return output

    @staticmethod
    def _nearest_record_for_path(
        path: tuple[str, ...],
        records: Sequence[_SectionRecord],
    ) -> _SectionRecord | None:
        candidate: _SectionRecord | None = None
        candidate_index = -1
        for index, record in enumerate(records):
            if record.path == path and index > candidate_index:
                candidate = record
                candidate_index = index
        return candidate

    @classmethod
    def _parent_representative_id(
        cls,
        record: _SectionRecord,
        records: Sequence[_SectionRecord],
        representatives: Mapping[str, str],
    ) -> str | None:
        parent_path = record.parent_path
        while parent_path:
            parent = cls._nearest_record_for_path(parent_path, records)
            if parent is not None and parent.section_id in representatives:
                return representatives[parent.section_id]
            parent_path = parent_path[:-1]
        return record.section.parent_section_id


# Names that make the implementation easy to discover from an integration.
StructureAwareChunker = DeterministicChunker
Chunker = DeterministicChunker


__all__ = [
    "Chunker",
    "ChunkingConfig",
    "DeterministicChunker",
    "StructureAwareChunker",
    "content_hash_for_sections",
    "content_hash_for_chunk",
    "stable_chunk_id",
    "stable_lineage_key",
    "stable_section_id",
]
