import unittest

from rag_service.api.container import build_application
from rag_service.domain import DocumentSection


class GenerationTests(unittest.IsolatedAsyncioTestCase):
    async def test_generator_abstains_without_matching_evidence(self) -> None:
        application = build_application()
        application.ingest(
            "manual",
            [DocumentSection(text="The device uses a blue status light when ready.")],
            "v1",
        )

        _, answer = await application.answer(
            "What is the emergency evacuation route?",
            top_k=1,
            candidate_k=5,
            alpha=0.5,
        )

        self.assertTrue(answer.abstained)
        self.assertEqual(answer.citations, ())


if __name__ == "__main__":
    unittest.main()
