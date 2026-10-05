"""Offline checks for human-readable, model-authored drafts; no generation."""

from __future__ import annotations

import hashlib
import re
from collections import Counter, defaultdict
from typing import Any

from .corpus import SourceRecord
from .families import family_map, isolation_errors
from .gold import gold_version_map
from .validation import TARGET_COUNTS

MODEL = "omnirush/gpt-6-astra"
_META = re.compile(r"\b(?:the|this|given|provided|above)\s+(?:passage|text|section)\b", re.I)
_FILLER = re.compile(
    r"\b(?:placeholder|TODO|TBD|lorem ipsum|variant\s*\d+)\b|"
    r"what (?:does .* (?:say|state)|is (?:stated|mentioned|documented))\??$|"
    r"which (?:exact )?identifier is (?:named|shown)|what (?:row is listed|changed in)", re.I,
)
_VAGUE = re.compile(
    r"^(?:what is (?:the (?:default )?value|it|this|that)|"
    r"how does (?:it|this|that) work|what can you tell me about (?:it|this|that))\?$", re.I,
)


def normalized(text: str) -> str:
    return " ".join(text.split())


def exact_span(text: str, quote: str) -> tuple[str, int, int] | None:
    """Locate whitespace-equivalent evidence and return the original source span."""
    words = quote.split()
    if not words:
        return None
    match = re.search(r"\s+".join(re.escape(word) for word in words), text)
    return (match.group(), match.start(), match.end()) if match else None


class DraftImporter:
    def __init__(
        self, records: list[SourceRecord], assignments: dict[str, str],
        diffs: list[dict[str, Any]] | None = None, acl: dict[str, Any] | None = None,
    ) -> None:
        self.records = records
        self.assignments = assignments
        mapping = family_map(records)
        errors = isolation_errors({k: v for k, v in assignments.items() if k in mapping}, mapping)
        if errors:
            raise ValueError(errors[0])
        self.sources: dict[tuple[str, str], list[SourceRecord]] = defaultdict(list)
        texts: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))
        for record in records:
            self.sources[record.lineage_key, record.version].append(record)
            texts[record.lineage_key][record.version].append(record.text)
        self.diffs = {str(d["id"]): d for d in (diffs or [])}
        changed = {str(d["lineage_key"]) for d in (diffs or [])}
        self.stable = {
            key for key, versions in texts.items()
            if key not in changed and len({tuple(v) for v in versions.values()}) == 1
        }
        self.acl = acl or {}
        self.gold = gold_version_map(records)
        self.corpus_text = "\n".join(r.text for r in records).casefold()

    def accept(self, draft: dict[str, Any], seen: set[str]) -> dict[str, Any]:
        question = str(draft.get("question", "")).strip()
        key = normalized(question).casefold()
        if key in seen:
            raise ValueError("duplicate question")
        if _META.search(question):
            raise ValueError("question refers to passage/text/section")
        if (_FILLER.search(question) or _VAGUE.search(question)
                or len(question.split()) < 5 or not question.endswith("?")):
            raise ValueError("placeholder or vague question")
        kind = draft.get("type")
        if kind not in TARGET_COUNTS:
            raise ValueError("unknown question type")
        lineage = str(draft.get("lineage_key", ""))
        split = self.assignments.get(lineage)
        if split not in {"dev", "test"}:
            raise ValueError("primary lineage is not dev/test")
        version = str(draft.get("target_version", ""))
        if version not in {"pg-15", "pg-16", "pg-17"}:
            raise ValueError("unsupported target version")
        for flag in ("paraphrased", "version_independent"):
            if not isinstance(draft.get(flag), bool):
                raise ValueError(f"{flag} must be boolean")
        answer = draft.get("expected_answer")
        if not isinstance(answer, str) or not answer.strip():
            raise ValueError("missing expected answer")
        answerable = kind not in {"unanswerable", "version_unavailable"}
        evidence = draft.get("evidence_spans", [])
        spans: list[dict[str, Any]] = []
        if answerable and not evidence:
            evidence = [{"lineage_key": lineage, "version": version,
                         "quote": draft.get("evidence_quote", "")}]
        for value in evidence:
            source_key = str(value.get("lineage_key", lineage))
            source_version = str(value.get("version", version))
            if self.assignments.get(source_key) not in {"dev", "test"}:
                raise ValueError("evidence lineage is not dev/test")
            if self.assignments[source_key] != split:
                raise ValueError("evidence crosses dev/test split")
            if kind != "unchanged_control" and source_version != version:
                raise ValueError("evidence version differs from target")
            found = None
            for record in self.sources.get((source_key, source_version), []):
                match = exact_span(record.text, str(value.get("quote", "")))
                if match:
                    found = (record, match)
                    break
            if found is None:
                raise ValueError("quote absent from full source")
            record, (quote, start, end) = found
            if kind == "table" and record.kind != "table":
                raise ValueError("table question requires a table source")
            if kind == "acl" and not any(
                title.casefold() in " / ".join(record.section_path).casefold()
                for title in self.acl.get("restricted_section_titles", [])
            ):
                raise ValueError("ACL source is not restricted")
            if draft["version_independent"] and source_key not in self.stable:
                raise ValueError("version-independent source has changed")
            spans.append({
                "lineage_key": source_key, "version": source_version, "quote": quote,
                "source_file": record.source_file, "source_line": record.source_line,
                "section_id": record.section_id, "section_path": list(record.section_path),
                "kind": record.kind, "start_char": start, "end_char": end,
                "gold_versions": (self.gold[source_key, source_version]
                                  if draft["version_independent"] else []),
            })
        if answerable and not spans:
            raise ValueError("answerable question requires evidence")
        if kind == "multi_hop" and (
            len(spans) != 2 or len({s["lineage_key"] for s in spans}) != 2
        ):
            raise ValueError("multi-hop requires two distinct sections")
        if not draft["version_independent"] and answerable:
            if not re.search(rf"\bPostgreSQL {version[3:]}\b", question):
                raise ValueError("version-dependent question must name PostgreSQL version")
        if kind in {"version_specific", "unchanged_control", "version_unavailable"}:
            diff = self.diffs.get(str(draft.get("diff_id", "")))
            if not diff or diff["lineage_key"] != lineage or not any(
                c["kind"] != "text_changed" for c in diff["changes"]
            ):
                raise ValueError("missing specialized diff provenance")
            if kind == "unchanged_control" and (
                len(spans) != 2 or len({s["version"] for s in spans}) != 2
                or len({normalized(s["quote"]) for s in spans}) != 1
            ):
                raise ValueError("control needs identical evidence in two versions")
        if not answerable:
            if answer != "Not answerable" or spans or draft.get("evidence_quote", "") != "":
                raise ValueError("unanswerable requires Not answerable and empty evidence")
            identifier = str(draft.get("invented_identifier", ""))
            unavailable = str(draft.get("unavailable_identifier", ""))
            if identifier:
                if identifier.casefold() not in question.casefold():
                    raise ValueError("invented identifier absent from question")
                if identifier.casefold() in self.corpus_text:
                    raise ValueError("invented identifier occurs in corpus")
            elif unavailable:
                if unavailable.casefold() not in question.casefold():
                    raise ValueError("unavailable identifier absent from question")
                if unavailable.casefold() not in self.corpus_text:
                    raise ValueError("unavailable identifier does not exist in any version")
                if any(unavailable.casefold() in r.text.casefold()
                       for r in self.records if r.version == version):
                    raise ValueError("unavailable identifier exists in requested version")
            else:
                raise ValueError("unanswerable requires an absence-check identifier")
        acl_allowance = True
        if kind == "acl":
            requester = draft.get("requester")
            principals = {p["id"]: p for p in self.acl.get("principals", [])}
            if requester in self.acl.get("restricted_requesters", []):
                acl_allowance = False
            elif requester in principals and set(principals[requester].get("groups", [])) & set(
                self.acl.get("restricted_allowed_groups", [])
            ):
                acl_allowance = True
            else:
                raise ValueError("ACL requester has no configured policy")
            if draft.get("acl_allowance", acl_allowance) != acl_allowance:
                raise ValueError("ACL allowance disagrees with requester policy")
        gold_versions = (sorted(set.intersection(*(set(s["gold_versions"]) for s in spans)))
                         if draft["version_independent"] and spans else [])
        digest = hashlib.sha256(key.encode()).hexdigest()[:16]
        row = dict(draft)
        row.update({
            "id": f"draft-{digest}", "question": question, "split": split,
            "author": "llm_drafted", "drafted_by": MODEL, "validated": False,
            "answerability": answerable, "evidence_spans": spans,
            "evidence_quote": ([s["quote"] for s in spans] if len(spans) > 1
                               else spans[0]["quote"] if spans else ""),
            "requester": draft.get("requester", "benchmark-user"),
            "acl_allowance": acl_allowance, "gold_versions": gold_versions,
        })
        seen.add(key)
        return row

    def import_batch(
        self, drafts: list[dict[str, Any]], existing: list[dict[str, Any]],
    ) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        seen = {normalized(row["question"]).casefold() for row in existing}
        accepted = []
        discarded = []
        for index, draft in enumerate(drafts, 1):
            try:
                accepted.append(self.accept(draft, seen))
            except (ValueError, TypeError, KeyError) as exc:
                discarded.append({"row": index, "type": draft.get("type"), "reason": str(exc)})
        return accepted, {
            "accepted": len(accepted), "discarded": len(discarded),
            "accepted_by_type": dict(Counter(row["type"] for row in accepted)),
            "discarded_by_type": dict(Counter(row["type"] for row in discarded)),
            "reasons": discarded,
        }
