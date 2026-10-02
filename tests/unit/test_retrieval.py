import unittest

from rag_service.api.container import build_application
from rag_service.domain import AccessPolicy, DocumentSection
from rag_service.retrieval import RetrievalFilters


class RetrievalTests(unittest.IsolatedAsyncioTestCase):
    async def test_exact_identifier_is_retrievable(self) -> None:
        application = build_application()
        application.ingest(
            "manual",
            [
                DocumentSection(text="The approved replacement is SKU-994X."),
                DocumentSection(text="The warranty lasts two years."),
            ],
            "v1",
        )

        prepared, answer = await application.answer(
            "Which replacement is SKU-994X?",
            top_k=2,
            candidate_k=10,
            alpha=0.35,
        )

        self.assertFalse(answer.abstained)
        self.assertEqual(prepared.matches[0].chunk.text, "The approved replacement is SKU-994X.")
        self.assertEqual(answer.citations[0].chunk_id, prepared.matches[0].chunk.chunk_id)

    async def test_document_acl_is_applied_before_ranking(self) -> None:
        application = build_application()
        application.ingest(
            "restricted",
            [DocumentSection(text="The confidential launch date is November 15.")],
            "v1",
            access_policy=AccessPolicy(principals=("alice",)),
        )
        application.ingest(
            "public",
            [DocumentSection(text="The public launch guide is available today.")],
            "v1",
        )

        hidden = await application.retriever.retrieve(
            "launch date",
            top_k=5,
            candidate_k=10,
            alpha=0.5,
            filters=RetrievalFilters(principal="bob"),
        )
        visible = await application.retriever.retrieve(
            "launch date",
            top_k=5,
            candidate_k=10,
            alpha=0.5,
            filters=RetrievalFilters(principal="alice"),
        )

        self.assertNotIn("restricted", {match.chunk.document_id for match in hidden})
        self.assertIn("restricted", {match.chunk.document_id for match in visible})

    async def test_acl_filtering_precedes_candidate_limit(self) -> None:
        application = build_application()
        application.ingest(
            "restricted",
            [DocumentSection(text="The confidential launch date is November 15.")],
            "v1",
            access_policy=AccessPolicy(principals=("alice",)),
        )
        application.ingest(
            "public",
            [DocumentSection(text="The public launch date is published in the guide.")],
            "v1",
        )

        matches = await application.retriever.retrieve(
            "confidential launch date",
            top_k=1,
            candidate_k=1,
            alpha=0.5,
            filters=RetrievalFilters(principal="bob"),
        )

        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].chunk.document_id, "public")

    async def test_group_acl_is_checked_for_denied_and_allowed_groups(self) -> None:
        application = build_application()
        application.ingest(
            "operations",
            [DocumentSection(text="The operations group runbook contains the launch plan.")],
            "v1",
            access_policy=AccessPolicy(groups=("operations",)),
        )

        denied = await application.retriever.retrieve(
            "launch plan",
            top_k=1,
            candidate_k=1,
            alpha=0.5,
            filters=RetrievalFilters(principal="bob", groups=("sales",)),
        )
        allowed = await application.retriever.retrieve(
            "launch plan",
            top_k=1,
            candidate_k=1,
            alpha=0.5,
            filters=RetrievalFilters(principal="bob", groups=("operations",)),
        )

        self.assertEqual(denied, ())
        self.assertEqual([match.chunk.document_id for match in allowed], ["operations"])


if __name__ == "__main__":
    unittest.main()
