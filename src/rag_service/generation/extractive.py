"""A transparent answer generator for running the service without an LLM key."""

from __future__ import annotations

import asyncio
import re
from collections.abc import AsyncIterator

from rag_service.retrieval.encoders import tokenize

from .models import GeneratedAnswer, GenerationRequest

_SENTENCE_RE = re.compile(r"(?<=[.!?])\s+")
_STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "do",
    "does",
    "for",
    "how",
    "i",
    "is",
    "it",
    "of",
    "on",
    "or",
    "the",
    "to",
    "was",
    "what",
    "when",
    "where",
    "which",
    "who",
    "why",
    "with",
    "you",
}


class ExtractiveAnswerGenerator:
    """Return short evidence excerpts instead of pretending to be an LLM.

    This makes the local API honest and useful.  A hosted generator can later
    implement the same contract and consume :func:`build_grounded_prompt`.
    """

    def __init__(self, *, minimum_score: float = 0.12, max_citations: int = 3) -> None:
        if not 0 <= minimum_score <= 1:
            raise ValueError("minimum_score must be between zero and one")
        if max_citations < 1:
            raise ValueError("max_citations must be positive")
        self.minimum_score = minimum_score
        self.max_citations = max_citations

    async def generate(self, request: GenerationRequest) -> GeneratedAnswer:
        return self._generate(request)

    async def stream(self, request: GenerationRequest) -> AsyncIterator[str]:
        answer = self._generate(request).answer
        words = answer.split(" ")
        for index, word in enumerate(words):
            if index:
                yield " "
            yield word
            await asyncio.sleep(0)

    def _generate(self, request: GenerationRequest) -> GeneratedAnswer:
        usable = [match for match in request.matches if match.final_score >= self.minimum_score]
        if not usable:
            return GeneratedAnswer(
                answer=(
                    "I couldn't find enough matching evidence in the indexed documents "
                    "to answer that confidently."
                ),
                confidence=0.0,
                abstained=True,
            )

        query_terms = set(tokenize(request.query))
        meaningful_terms = query_terms.difference(_STOPWORDS)
        usable = [
            match
            for match in usable
            if meaningful_terms.intersection(tokenize(match.chunk.text))
        ]
        if not usable:
            return GeneratedAnswer(
                answer=(
                    "I couldn't find enough matching evidence in the indexed documents "
                    "to answer that confidently."
                ),
                confidence=0.0,
                abstained=True,
            )
        excerpts: list[str] = []
        for match in usable[: self.max_citations]:
            sentence = self._best_sentence(match.chunk.text, query_terms)
            if sentence and sentence not in excerpts:
                excerpts.append(sentence)
        if not excerpts:
            excerpts = [match.chunk.text.strip() for match in usable[: self.max_citations]]

        answer = "Based on the indexed evidence: " + " ".join(excerpts)
        return GeneratedAnswer(
            answer=answer,
            citations=tuple(match.citation() for match in usable[: self.max_citations]),
            confidence=max(0.0, min(1.0, usable[0].final_score)),
            abstained=False,
        )

    @staticmethod
    def _best_sentence(text: str, query_terms: set[str]) -> str:
        sentences = [part.strip() for part in _SENTENCE_RE.split(text) if part.strip()]
        if not sentences:
            return text.strip()
        return max(
            sentences,
            key=lambda sentence: (
                len(query_terms.intersection(tokenize(sentence))),
                -len(sentence),
            ),
        )


__all__ = ["ExtractiveAnswerGenerator"]
