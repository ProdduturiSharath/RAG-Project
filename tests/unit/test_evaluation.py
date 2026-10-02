import unittest

from rag_service.api.container import build_application
from rag_service.domain import DocumentSection
from rag_service.evaluation import EvaluationCase, evaluate_retrieval


class EvaluationTests(unittest.IsolatedAsyncioTestCase):
    async def test_retrieval_metrics_make_misses_visible(self) -> None:
        application = build_application()
        result = application.ingest(
            "manual",
            [DocumentSection(text="Use SKU-994X for the replacement filter.")],
            "v1",
        )
        chunk_id = result.chunks[0].chunk_id

        summary = await evaluate_retrieval(
            application.retriever,
            [EvaluationCase("Which replacement filter is approved?", {chunk_id})],
            top_k=1,
            candidate_k=5,
        )

        self.assertEqual(summary.cases, 1)
        self.assertEqual(summary.recall_at_k, 1.0)
        self.assertEqual(summary.mean_reciprocal_rank, 1.0)
        self.assertEqual(summary.misses, ())


if __name__ == "__main__":
    unittest.main()
