import unittest

from rag_service.domain import AccessPolicy, Chunk, SourceLocation
from rag_service.retrieval import PineconeHybridIndex, RetrievalFilters


class FakePineconeIndex:
    def __init__(self) -> None:
        self.upsert_call = None
        self.query_call = None

    def upsert(self, **kwargs):
        self.upsert_call = kwargs

    def query(self, **kwargs):
        self.query_call = kwargs
        return {
            "matches": [
                {
                    "id": "chunk-1",
                    "score": 0.9,
                    "metadata": {
                        "document_id": "manual",
                        "version": "v1",
                        "text": "SKU-994X is approved.",
                        "acl_public": False,
                        "acl_principals": ["alice"],
                        "acl_groups": [],
                        "section_path": "[\"Maintenance\"]",
                        "page_number": 4,
                    },
                }
            ]
        }


class ProviderAdapterTests(unittest.TestCase):
    def test_pinecone_adapter_scales_query_and_round_trips_metadata(self) -> None:
        client = FakePineconeIndex()
        adapter = PineconeHybridIndex(client, namespace="test")
        chunk = Chunk(
            chunk_id="chunk-1",
            document_id="manual",
            version="v1",
            text="SKU-994X is approved.",
            section_path=("Maintenance",),
            page_number=4,
            source=SourceLocation(uri="manual.pdf"),
            access_policy=AccessPolicy(principals=("alice",)),
        )

        adapter.upsert(
            [chunk],
            dense_vectors=[(1.0, 0.0)],
            sparse_vectors=[{"sku-994x": 2.0}],
        )
        results = adapter.search(
            (1.0, 0.0),
            {"sku-994x": 2.0},
            top_k=3,
            alpha=0.7,
            filters=RetrievalFilters(principal="alice"),
        )

        self.assertEqual(client.upsert_call["namespace"], "test")
        vector = client.upsert_call["vectors"][0]
        self.assertEqual(
            vector["sparse_values"]["indices"],
            sorted(vector["sparse_values"]["indices"]),
        )
        self.assertAlmostEqual(client.query_call["vector"][0], 0.7)
        self.assertAlmostEqual(client.query_call["sparse_vector"]["values"][0], 0.6)
        self.assertEqual(client.query_call["filter"]["$or"][1]["acl_principals"]["$in"], ["alice"])
        self.assertEqual(results[0].chunk.document_id, "manual")
        self.assertEqual(results[0].chunk.page_number, 4)


if __name__ == "__main__":
    unittest.main()
