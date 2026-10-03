"""Small immutable domain objects for document ingestion.

The domain layer deliberately does not know about a vector database, an
embedding provider, or a particular parser.  Values in this module are plain
Python data and are consequently easy to persist, test, and pass between
adapters.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Literal


def _copy_metadata(value: Mapping[str, Any] | None) -> dict[str, Any]:
    """Return a shallow copy so callers cannot mutate a frozen model in place."""

    return dict(value or {})


@dataclass(frozen=True, slots=True)
class SourceLocation:
    """Where a document or a section came from.

    ``uri`` is the preferred stable identifier.  ``path`` is provided for
    local-file adapters that have a path but no URI yet.  Either one may be
    supplied.  Page and line information is optional because many sources do
    not expose it.
    """

    uri: str = ""
    path: str | None = None
    page_number: int | None = None
    line_start: int | None = None
    line_end: int | None = None
    fragment: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.uri and not self.path:
            raise ValueError("SourceLocation requires a uri or path")
        if self.page_number is not None and self.page_number < 1:
            raise ValueError("page_number must be positive when supplied")
        if self.line_start is not None and self.line_start < 1:
            raise ValueError("line_start must be positive when supplied")
        if self.line_end is not None and self.line_end < 1:
            raise ValueError("line_end must be positive when supplied")
        if (
            self.line_start is not None
            and self.line_end is not None
            and self.line_end < self.line_start
        ):
            raise ValueError("line_end cannot precede line_start")
        object.__setattr__(self, "metadata", _copy_metadata(self.metadata))

    @property
    def page(self) -> int | None:
        """Short alias used by parsers and serializers."""

        return self.page_number

    @property
    def stable_uri(self) -> str:
        """Return the best available stable source identifier."""

        return self.uri or self.path or ""


@dataclass(frozen=True, slots=True)
class AccessPolicy:
    """Simple document-level read policy.

    More sophisticated authorization belongs in an application adapter.  The
    model intentionally supports the common cases (public documents,
    principals, and groups) and keeps arbitrary policy attributes intact.
    """

    public: bool = False
    principals: tuple[str, ...] = ()
    groups: tuple[str, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "principals", tuple(self.principals))
        object.__setattr__(self, "groups", tuple(self.groups))
        object.__setattr__(self, "metadata", _copy_metadata(self.metadata))

    @property
    def is_public(self) -> bool:
        return self.public

    def allows(
        self,
        principal: str | None = None,
        *,
        groups: tuple[str, ...] | list[str] = (),
    ) -> bool:
        """Return whether a principal may read this document.

        An empty policy is intentionally private.  ``*`` is accepted as a
        convenient wildcard for adapters that use ACL-style values.
        """

        if self.public or "*" in self.principals or "*" in self.groups:
            return True
        if principal and principal in self.principals:
            return True
        return bool(set(groups).intersection(self.groups))


@dataclass(frozen=True, slots=True)
class DocumentIdentity:
    """Stable identity for a logical document across content revisions."""

    document_id: str
    source: SourceLocation | None = None
    title: str | None = None
    access_policy: AccessPolicy | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.document_id.strip():
            raise ValueError("document_id cannot be empty")
        object.__setattr__(self, "metadata", _copy_metadata(self.metadata))

    @property
    def id(self) -> str:
        return self.document_id

    @property
    def source_location(self) -> SourceLocation | None:
        return self.source


@dataclass(frozen=True, slots=True)
class DocumentVersion:
    """A concrete revision of a document.

    ``content_hash`` should normally be a SHA-256 digest.  The model does not
    enforce an algorithm so callers can migrate hashing strategies without
    changing the domain API.
    """

    document_id: str
    version: str
    content_hash: str
    source: SourceLocation | None = None
    created_at: datetime | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.document_id.strip():
            raise ValueError("document_id cannot be empty")
        if not self.version.strip():
            raise ValueError("version cannot be empty")
        if not self.content_hash.strip():
            raise ValueError("content_hash cannot be empty")
        object.__setattr__(self, "metadata", _copy_metadata(self.metadata))

    @property
    def version_id(self) -> str:
        return self.version

    @property
    def product_version(self) -> str:
        """The searchable product scope represented by ``version``."""

        return self.version

    @property
    def idempotency_key(self) -> str:
        return f"{self.document_id}:{self.version}:{self.content_hash}"


@dataclass(frozen=True, slots=True)
class DocumentSection:
    """A parsed structural section supplied to the chunker.

    ``section_path`` is preferred when a parser already knows the hierarchy.
    If it is empty, the chunker infers a path from ``heading`` and ``level``.
    ``page_metadata`` is kept separate from general metadata so page-level
    details can be copied to every resulting chunk without being flattened or
    discarded.
    """

    text: str
    heading: str | None = None
    level: int = 0
    section_path: tuple[str, ...] = ()
    page_number: int | None = None
    page_metadata: Mapping[str, Any] = field(default_factory=dict)
    metadata: Mapping[str, Any] = field(default_factory=dict)
    section_id: str | None = None
    parent_section_id: str | None = None
    source: SourceLocation | None = None
    lineage_key: str | None = None
    kind: Literal["text", "table", "code"] = "text"

    def __post_init__(self) -> None:
        if self.level < 0:
            raise ValueError("section level cannot be negative")
        if self.page_number is not None and self.page_number < 1:
            raise ValueError("page_number must be positive when supplied")
        if self.kind not in {"text", "table", "code"}:
            raise ValueError("section kind must be text, table, or code")
        object.__setattr__(self, "section_path", tuple(self.section_path))
        object.__setattr__(self, "page_metadata", _copy_metadata(self.page_metadata))
        object.__setattr__(self, "metadata", _copy_metadata(self.metadata))

    @property
    def path(self) -> tuple[str, ...]:
        """Alias for ``section_path`` used by some parser adapters."""

        return self.section_path

    @property
    def page(self) -> int | None:
        return self.page_number


# A descriptive alias makes parser signatures read naturally while keeping a
# single runtime type for callers.
ParsedSection = DocumentSection


@dataclass(frozen=True, slots=True)
class Chunk:
    """A deterministic retrieval unit produced from a document section."""

    chunk_id: str
    document_id: str
    version: str
    text: str
    section_path: tuple[str, ...] = ()
    ordinal: int = 0
    parent_id: str | None = None
    child_ids: tuple[str, ...] = ()
    page_number: int | None = None
    page_metadata: Mapping[str, Any] = field(default_factory=dict)
    metadata: Mapping[str, Any] = field(default_factory=dict)
    source: SourceLocation | None = None
    section_id: str | None = None
    access_policy: AccessPolicy | None = None
    kind: Literal["text", "table", "code"] = "text"
    content_hash: str | None = None
    lineage_key: str | None = None
    revision: int = 1
    parent_text: str | None = None

    def __post_init__(self) -> None:
        if not self.chunk_id.strip():
            raise ValueError("chunk_id cannot be empty")
        if not self.document_id.strip():
            raise ValueError("document_id cannot be empty")
        if not self.version.strip():
            raise ValueError("version cannot be empty")
        if self.ordinal < 0:
            raise ValueError("ordinal cannot be negative")
        if self.page_number is not None and self.page_number < 1:
            raise ValueError("page_number must be positive when supplied")
        if self.kind not in {"text", "table", "code"}:
            raise ValueError("chunk kind must be text, table, or code")
        object.__setattr__(self, "section_path", tuple(self.section_path))
        object.__setattr__(self, "child_ids", tuple(self.child_ids))
        object.__setattr__(self, "page_metadata", _copy_metadata(self.page_metadata))
        object.__setattr__(self, "metadata", _copy_metadata(self.metadata))

    @property
    def id(self) -> str:
        return self.chunk_id

    @property
    def content(self) -> str:
        return self.text

    @property
    def page(self) -> int | None:
        return self.page_number

    @property
    def children(self) -> tuple[str, ...]:
        return self.child_ids

    @property
    def product_version(self) -> str:
        """The searchable product scope represented by ``version``."""

        return self.version


@dataclass(frozen=True, slots=True)
class IngestionResult:
    """Outcome of one deterministic ingestion operation."""

    document_id: str
    version: str
    content_hash: str
    chunks: tuple[Chunk, ...] = ()
    ingestion_id: str | None = None
    source: SourceLocation | None = None
    access_policy: AccessPolicy | None = None
    already_ingested: bool = False
    errors: tuple[str, ...] = ()
    dense_vectors: tuple[tuple[float, ...], ...] = ()
    sparse_vectors: tuple[Mapping[str, float], ...] = ()
    revision: int = 1

    def __post_init__(self) -> None:
        if not self.document_id.strip():
            raise ValueError("document_id cannot be empty")
        if not self.version.strip():
            raise ValueError("version cannot be empty")
        if not self.content_hash.strip():
            raise ValueError("content_hash cannot be empty")
        object.__setattr__(self, "chunks", tuple(self.chunks))
        object.__setattr__(self, "errors", tuple(self.errors))
        object.__setattr__(
            self,
            "dense_vectors",
            tuple(tuple(float(value) for value in vector) for vector in self.dense_vectors),
        )
        object.__setattr__(
            self,
            "sparse_vectors",
            tuple(dict(vector) for vector in self.sparse_vectors),
        )

    @property
    def chunk_count(self) -> int:
        return len(self.chunks)

    @property
    def is_empty(self) -> bool:
        return not self.chunks

    @property
    def idempotency_key(self) -> str:
        return f"{self.document_id}:{self.version}:{self.content_hash}"

    @property
    def version_id(self) -> str:
        return self.version

    @property
    def product_version(self) -> str:
        """The searchable product scope represented by ``version``."""

        return self.version
