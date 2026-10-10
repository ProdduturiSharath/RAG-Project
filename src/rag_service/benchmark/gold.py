"""Version equivalence from exact full-source text, independent of retrieval."""

from collections import defaultdict

from .corpus import SourceRecord


def gold_version_map(records: list[SourceRecord]) -> dict[tuple[str, str], list[str]]:
    grouped: dict[str, dict[str, list[tuple[str, str]]]] = defaultdict(lambda: defaultdict(list))
    for record in records:
        grouped[record.lineage_key][record.version].append((record.kind, record.text))
    result = {}
    for lineage, versions in grouped.items():
        for version, texts in versions.items():
            result[lineage, version] = sorted(
                other for other, other_texts in versions.items()
                if sorted(texts) == sorted(other_texts)
            )
    return result
