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

    async def test_citation_exposes_product_version_and_section_path(self) -> None:
        application = build_application()
        application.ingest(
            "manual",
            [DocumentSection(text="Set max_wal_senders to 20.", heading="Replication", level=1)],
            "pg17",
        )

        prepared, answer = await application.answer(
            "What is max_wal_senders?", top_k=1, candidate_k=5, alpha=0.5
        )

        self.assertFalse(answer.abstained)
        self.assertEqual(answer.citations[0].product_version, "pg17")
        self.assertEqual(answer.citations[0].section_path, ("Replication",))
        self.assertEqual(prepared.matches[0].citation().revision, 1)


if __name__ == "__main__":
    unittest.main()
