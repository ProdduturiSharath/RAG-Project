"""Deterministic version selection over authorized, active version labels."""

import re
from collections.abc import Mapping, Sequence
from dataclasses import replace

from .models import RetrievalFilters, ScopeResult


def version_key(value: str) -> tuple[tuple[int, int | str], ...]:
    return tuple((1, int(part)) if part.isdigit() else (0, part.casefold())
                 for part in re.split(r"(\d+)", value))


def resolve_scope(
    query: str, filters: RetrievalFilters, available: Mapping[str, Sequence[str]],
    default_mode: str = "none",
) -> ScopeResult:
    mode = filters.version_mode or ("explicit" if filters.product_version else default_mode)
    labels = tuple(sorted(
        {v for versions in available.values() for v in versions}, key=version_key
    ))
    if mode == "none" or (mode == "explicit" and filters.version_selector == "all"):
        return ScopeResult(replace(filters, product_version=None, scopes=None), versions=labels)
    if mode == "explicit":
        if filters.version_selector == "latest":
            scopes = tuple((doc, max(versions, key=version_key))
                           for doc, versions in sorted(available.items()) if versions)
            return ScopeResult(replace(filters, product_version=None, scopes=scopes),
                               versions=tuple(sorted({v for _, v in scopes}, key=version_key)))
        if not filters.product_version:
            raise ValueError("explicit exact scope requires product_version")
        return ScopeResult(filters, versions=(filters.product_version,))
    # Bare numbers in prose are not version claims. Recognize catalog labels,
    # PostgreSQL/pg/version/v prefixes, and report multi-version questions explicitly.
    mentions = set(re.findall(r"\b(?:postgresql\s*|pg\s*|version\s+|v)(\d+(?:\.\d+)*)\b",
                              query, flags=re.IGNORECASE))
    matched = [v for v in labels if re.search(r"(?<!\w)" + re.escape(v) + r"(?!\w)",
                                             query, flags=re.IGNORECASE)
               or re.sub(r"^(?:postgresql\s*|pg|v)", "", v, flags=re.IGNORECASE) in mentions]
    choices = tuple(matched) if matched else labels
    if len(choices) != 1 or (mentions and not matched):
        return ScopeResult(replace(filters, scopes=()), "ambiguous", choices)
    return ScopeResult(replace(filters, product_version=choices[0]), versions=choices)
