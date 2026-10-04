import unittest
from typing import Any

from rag_service.domain import AccessPolicy, Chunk, SourceLocation
from rag_service.retrieval import (
    CrossEncoderReranker,
    PineconeHybridIndex,
    RetrievalFilters,
    ScoredChunk,
    SentenceTransformerEncoder,
)


class FakePineconeIndex:
    def __init__(self) -> None:
        self.upsert_call: dict[str, Any] | None = None
        self.query_call: dict[str, Any] | None = None

    def upsert(self, **kwargs: Any) -> None:
        self.upsert_call = kwargs

    def query(self, **kwargs: Any) -> dict[str, Any]:
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


class FakeSentenceModel:
    def __init__(self) -> None:
        self.inputs: list[str] = []

    def get_sentence_embedding_dimension(self) -> int:
        return 3

    def encode(self, texts: list[str], **_: Any) -> list[list[float]]:
        self.inputs.extend(texts)
        return [[1.0, 0.0, 0.0] for _ in texts]


class FakeCrossModel:
    def predict(self, pairs: list[tuple[str, str]], **_: Any) -> list[float]:
        return [float(len(text)) for _, text in pairs]


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

        self.assertIsNotNone(client.upsert_call)
        self.assertIsNotNone(client.query_call)
        upsert_call = client.upsert_call
        query_call = client.query_call
        assert upsert_call is not None
        assert query_call is not None
        self.assertEqual(upsert_call["namespace"], "test")
        vector = upsert_call["vectors"][0]
        self.assertEqual(
            vector["sparse_values"]["indices"],
            sorted(vector["sparse_values"]["indices"]),
        )
        self.assertAlmostEqual(query_call["vector"][0], 0.7)
        self.assertAlmostEqual(query_call["sparse_vector"]["values"][0], 0.6)
        self.assertEqual(query_call["filter"]["$or"][1]["acl_principals"]["$in"], ["alice"])
        self.assertEqual(results[0].chunk.document_id, "manual")
        self.assertEqual(results[0].chunk.page_number, 4)

    def test_sentence_transformer_adapter_supports_metadata_prefixes(self) -> None:
        model = FakeSentenceModel()
        adapter = SentenceTransformerEncoder(
            "fake", metadata_prefixed=True, model=model
        )
        chunk = Chunk(
            chunk_id="chunk-1",
            document_id="manual",
            version="pg17",
            text="max_wal_senders is 20.",
            section_path=("Replication",),
        )

        vectors = adapter.embed_chunks((chunk,))

        self.assertEqual(vectors, ((1.0, 0.0, 0.0),))
        self.assertIn("Document: manual", model.inputs[0])
        self.assertIn("Section: Replication", model.inputs[0])
        self.assertEqual(
            SentenceTransformerEncoder("bge-base", model=FakeSentenceModel()).model_name,
            "BAAI/bge-base-en-v1.5",
        )

    def test_cross_encoder_reranker_sets_scores_and_ranks(self) -> None:
        chunks = [
            Chunk(chunk_id="short", document_id="doc", version="v1", text="short"),
            Chunk(chunk_id="long", document_id="doc", version="v1", text="a longer match"),
        ]
        reranker = CrossEncoderReranker(model=FakeCrossModel())

        results = reranker.rerank(
            "match", tuple(ScoredChunk(chunk, hybrid_score=0.1) for chunk in chunks)
        )

        self.assertEqual(results[0].chunk.chunk_id, "long")
        self.assertEqual(results[0].rank, 1)
        self.assertIsNotNone(results[0].rerank_score)


if __name__ == "__main__":
    unittest.main()
