"""Small regression harness for retrieval quality, not just answer demos."""

from __future__ import annotations

from collections.abc import Collection, Iterable
from dataclasses import dataclass, field

from rag_service.retrieval import HybridRetriever, RetrievalFilters


@dataclass(frozen=True, slots=True)
class EvaluationCase:
    query: str
    relevant_chunk_ids: Collection[str] = ()
    expected_abstain: bool = False
    filters: RetrievalFilters | None = None

    def __post_init__(self) -> None:
        if not self.query.strip():
            raise ValueError("evaluation query cannot be empty")
        object.__setattr__(self, "relevant_chunk_ids", frozenset(self.relevant_chunk_ids))


@dataclass(frozen=True, slots=True)
class EvaluationSummary:
    cases: int
    recall_at_k: float
    mean_reciprocal_rank: float
    abstention_accuracy: float
    misses: tuple[str, ...] = field(default_factory=tuple)


async def evaluate_retrieval(
    retriever: HybridRetriever,
    cases: Iterable[EvaluationCase],
    *,
    top_k: int = 5,
    candidate_k: int = 30,
    alpha: float = 0.55,
) -> EvaluationSummary:
    """Run labeled cases and return metrics suitable for a regression check.

    ``recall_at_k`` is calculated per case as the fraction of labeled evidence
    IDs found in the returned set. Cases without labels are treated as
    abstention checks rather than silently inflating retrieval scores.
    """

    materialized = tuple(cases)
    if not materialized:
        return EvaluationSummary(0, 0.0, 0.0, 0.0)

    recall_values: list[float] = []
    reciprocal_ranks: list[float] = []
    abstention_hits = 0
    misses: list[str] = []

    for case in materialized:
        matches = await retriever.retrieve(
            case.query,
            top_k=top_k,
            candidate_k=candidate_k,
            alpha=alpha,
            filters=case.filters,
        )
        returned_ids = [match.chunk.chunk_id for match in matches]
        if case.relevant_chunk_ids:
            found = set(returned_ids).intersection(case.relevant_chunk_ids)
            recall_values.append(len(found) / len(case.relevant_chunk_ids))
            reciprocal_ranks.append(
                next(
                    (1.0 / rank for rank, chunk_id in enumerate(returned_ids, start=1)
                     if chunk_id in case.relevant_chunk_ids),
                    0.0,
                )
            )
            if not found:
                misses.append(case.query)
        else:
            # With no labeled evidence, an empty result is the only safe
            # retrieval behavior. Answer generation applies its own threshold.
            recall_values.append(1.0 if not matches else 0.0)
            reciprocal_ranks.append(0.0)

        did_abstain = not matches
        if did_abstain == case.expected_abstain:
            abstention_hits += 1

    return EvaluationSummary(
        cases=len(materialized),
        recall_at_k=sum(recall_values) / len(recall_values),
        mean_reciprocal_rank=sum(reciprocal_ranks) / len(reciprocal_ranks),
        abstention_accuracy=abstention_hits / len(materialized),
        misses=tuple(misses),
    )


__all__ = ["EvaluationCase", "EvaluationSummary", "evaluate_retrieval"]
