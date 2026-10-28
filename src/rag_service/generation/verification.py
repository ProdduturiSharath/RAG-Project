"""Deterministic quote checks and conservative lexical claim support (not entailment)."""

from __future__ import annotations

import re
from dataclasses import replace
from typing import Any

from rag_service.retrieval.models import Citation

from .models import Claim, GeneratedAnswer, GenerationRequest
from .prompting import authorized_request, contains_prompt_injection

STOPWORDS = frozenset(
    "a an the is are was were be to of in on for and or as by with it its "
    "this that from at which what how does do can have has will".split()
)
NEGATIONS = frozenset({"not", "no", "never", "cannot", "without", "disabled"})


def words(text: str) -> set[str]:
    return set(re.findall(r"\w+(?:\.\w+)*", text.casefold())) - STOPWORDS


def lexical_support(text: str, evidence: str) -> float:
    """Require identifiers, quantities and polarity as well as word overlap."""
    terms, source = words(text), words(evidence)
    if not terms:
        return 0.0
    required = {term for term in terms if "_" in term or re.search(r"\d", term)}
    if not required <= source:
        return 0.0
    if bool(terms & NEGATIONS) != bool(source & NEGATIONS):
        return 0.0
    return len(terms & source) / len(terms)


def quote_valid(citation: Citation, request: GenerationRequest) -> bool:
    return any(
        citation.chunk_id == chunk.chunk_id
        and citation.document_id == chunk.document_id
        and citation.version == chunk.version
        and citation.section_path == chunk.section_path
        and bool(citation.excerpt.strip())
        and not contains_prompt_injection(citation.excerpt)
        and not any(contains_prompt_injection(part) for part in citation.section_path)
        and citation.excerpt in chunk.text
        for chunk in (match.chunk for match in authorized_request(request).matches)
    )


def abstention(
    *,
    claims: tuple[Claim, ...] = (),
    reason: str = "insufficient_evidence",
    metadata: dict[str, Any] | None = None,
) -> GeneratedAnswer:
    return GeneratedAnswer(
        "not found",
        abstained=True,
        claims=tuple(replace(claim, included=False) for claim in claims),
        metadata={**(metadata or {}), "abstention_reason": reason},
    )


def decompose(answer: GeneratedAnswer) -> tuple[Claim, ...]:
    """Provider output is atomic already; split baseline prose into sentences."""
    if answer.claims:
        return answer.claims
    text = answer.answer.removeprefix("Based on the indexed evidence: ")
    parts = re.split(r"(?<=[.!?])\s+|\n+", text)
    return tuple(Claim(part.strip(), answer.citations) for part in parts if part.strip())


def annotate(answer: GeneratedAnswer, request: GenerationRequest) -> GeneratedAnswer:
    if answer.abstained or answer.answer.strip().casefold() == "not found":
        return abstention(metadata=answer.metadata)
    claims = []
    for claim in decompose(answer):
        valid = tuple(c for c in claim.citations if quote_valid(c, request))
        score = lexical_support(claim.text, " ".join(c.excerpt for c in valid))
        supported = (
            bool(valid)
            and len(valid) == len(claim.citations)
            and score >= 0.65
            and not contains_prompt_injection(claim.text)
        )
        claims.append(
            replace(
                claim,
                supported=supported,
                support_score=score,
                reason="lexical_support" if supported else "unsupported_or_bad_quote",
            )
        )
    return replace(answer, claims=tuple(claims))


def evidence_confidence(request: GenerationRequest) -> float:
    """Score usable evidence without reading gold labels or expected answers."""
    safe = authorized_request(request)
    if not safe.matches:
        return 0.0
    query_terms = words(request.query)
    identifiers = {t for t in query_terms if "_" in t}
    evidence = " ".join(match.chunk.text for match in safe.matches)
    if identifiers and not identifiers <= words(evidence):
        return 0.0
    coverage = len(query_terms & words(evidence)) / max(1, len(query_terms))
    return coverage * max(0.0, min(1.0, safe.matches[0].final_score))


def verify_answer(
    answer: GeneratedAnswer, request: GenerationRequest, *, threshold: float = 0.0
) -> GeneratedAnswer:
    marked = annotate(answer, request)
    if marked.abstained:
        return marked
    if evidence_confidence(request) <= threshold:
        return abstention(
            claims=marked.claims, reason="calibrated_evidence", metadata=answer.metadata
        )
    safe = authorized_request(request)
    versions = {m.chunk.version for m in safe.matches}
    version = answer.answered_version or request.answered_version
    if not version and len(versions) == 1:
        version = next(iter(versions))
    if not version or version not in versions:
        return abstention(claims=marked.claims, reason="wrong_version", metadata=answer.metadata)
    # Do not let uncatalogued free-form answer text bypass the claim verifier.
    rendered = " ".join(claim.text for claim in marked.claims if claim.included)
    original = answer.answer.removeprefix("Based on the indexed evidence: ")
    if " ".join(rendered.split()) != " ".join(original.split()):
        return abstention(claims=marked.claims, reason="unclaimed_text", metadata=answer.metadata)
    kept = tuple(
        c
        for c in marked.claims
        if c.included and c.supported and all(cite.version == version for cite in c.citations)
    )
    if not kept:
        return abstention(
            claims=marked.claims, reason="no_supported_claims", metadata=answer.metadata
        )
    citations = tuple(dict.fromkeys(cite for claim in kept for cite in claim.citations))
    return replace(
        marked,
        answer=" ".join(c.text for c in kept),
        claims=tuple(replace(c, included=c in kept) for c in marked.claims),
        citations=citations,
        answered_version=version,
        confidence=evidence_confidence(request),
        metadata={**answer.metadata, "stripped_claims": len(marked.claims) - len(kept)},
    )
