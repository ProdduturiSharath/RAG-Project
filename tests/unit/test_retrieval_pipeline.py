import unittest

from rag_service.domain import AccessPolicy, Chunk, DocumentSection
from rag_service.ingestion import DeterministicChunker
from rag_service.retrieval import (
    Bm25SparseEncoder,
    HashEmbeddingEncoder,
    InMemoryHybridIndex,
    RetrievalConfig,
    RetrievalFilters,
    ScoredChunk,
    bm25_search,
    fuse,
    resolve_scope,
)
from rag_service.retrieval.encoders import tokenize
from rag_service.retrieval.service import HybridRetriever


class RetrievalPipelineTests(unittest.IsolatedAsyncioTestCase):
    def _index(self) -> tuple[InMemoryHybridIndex, HashEmbeddingEncoder, Bm25SparseEncoder]:
        dense = HashEmbeddingEncoder(dimensions=32)
        sparse = Bm25SparseEncoder()
        index = InMemoryHybridIndex()
        chunks: list[Chunk] = []
        for version, text in (
            ("pg16", "PostgreSQL 16 sets max_wal_senders to 10."),
            ("pg17", "PostgreSQL 17 sets max_wal_senders to 20."),
        ):
            chunks.extend(DeterministicChunker(max_tokens=40, overlap_tokens=0).chunk(
                [DocumentSection(text=text, heading="Replication", level=1)],
                document_id="manual",
                version=version,
                access_policy=AccessPolicy(groups=("operations",)),
            ))
        index.upsert(
            chunks,
            dense_vectors=dense.embed(tuple(chunk.text for chunk in chunks)),
            sparse_vectors=sparse.encode(tuple(chunk.text for chunk in chunks)),
        )
        return index, dense, sparse

    async def test_pipeline_records_each_stage_and_applies_group_and_version_scope(self) -> None:
        index, dense, sparse = self._index()
        retriever = HybridRetriever(
            index,
            dense,
            sparse,
            config=RetrievalConfig(fusion="weighted", rerank_top_n=1),
        )

        result = await retriever.retrieve_detailed(
            "What does PostgreSQL 17 set for max_wal_senders?",
            top_k=1,
            candidate_k=2,
            alpha=0.5,
            filters=RetrievalFilters(
                principal="alice",
                groups=("operations",),
                product_version="pg17",
                version_mode="explicit",
            ),
        )

        self.assertEqual([match.chunk.version for match in result.matches], ["pg17"])
        self.assertEqual(
            [stage.stage for stage in result.stages],
            ["scope_auth", "dense", "sparse", "fusion", "rerank", "parent_context"],
        )
        self.assertEqual(set(index.traces), {result.trace_id})

    async def test_auto_scope_reports_ambiguity_instead_of_mixing_versions(self) -> None:
        index, dense, sparse = self._index()
        retriever = HybridRetriever(
            index, dense, sparse, config=RetrievalConfig(version_mode="auto")
        )

        result = await retriever.retrieve_detailed(
            "What is the sender limit?",
            top_k=1,
            candidate_k=2,
            filters=RetrievalFilters(groups=("operations",)),
        )

        self.assertEqual(result.matches, ())
        self.assertEqual(result.scope.status, "ambiguous")
        self.assertEqual(set(result.scope.versions), {"pg16", "pg17"})

    def test_sync_compatibility_path_uses_the_traced_pipeline(self) -> None:
        index, dense, sparse = self._index()
        retriever = HybridRetriever(index, dense, sparse)

        matches = retriever.retrieve_sync(
            "PostgreSQL 17 max_wal_senders", top_k=1, candidate_k=2,
            filters=RetrievalFilters(groups=("operations",), product_version="pg17"),
        )

        self.assertEqual([match.chunk.version for match in matches], ["pg17"])
        self.assertEqual(len(index.traces), 1)


class RetrievalPrimitiveTests(unittest.TestCase):
    def test_identifier_tokens_cover_exact_and_component_forms(self) -> None:
        tokens = set(tokenize("max_wal_senders pg.stat.activity AC-2(1)"))

        self.assertTrue({
            "max_wal_senders", "max", "wal", "senders", "pg.stat.activity",
            "pg", "stat", "activity", "ac-2(1)", "ac", "2", "1",
        }.issubset(tokens))

    def test_fusion_supports_rrf_and_normalized_weights(self) -> None:
        chunks = [
            DocumentSection(text="one"),
            DocumentSection(text="two"),
        ]
        built = DeterministicChunker(max_tokens=5, overlap_tokens=0).chunk(
            chunks, document_id="doc", version="v1"
        )
        dense = [ScoredChunk(built[0], dense_score=0.2), ScoredChunk(built[1], dense_score=1.0)]
        sparse = [ScoredChunk(built[0], sparse_score=1.0), ScoredChunk(built[1], sparse_score=0.2)]

        rrf = fuse(dense, sparse, method="rrf", alpha=0.5)
        weighted = fuse(dense, sparse, method="weighted", alpha=0.3)

        self.assertEqual({item.chunk.text for item in rrf}, {"one", "two"})
        self.assertEqual(weighted[0].chunk.text, "one")
        self.assertAlmostEqual(weighted[0].hybrid_score, 0.76)

    def test_bm25_baseline_uses_corpus_idf_and_document_length(self) -> None:
        chunks = DeterministicChunker(max_tokens=40, overlap_tokens=0).chunk(
            [
                DocumentSection(text="max_wal_senders controls replication senders."),
                DocumentSection(text="max setting is documented here."),
                DocumentSection(text="unrelated maintenance information."),
            ],
            document_id="doc",
            version="v1",
        )

        results = bm25_search("max_wal_senders", chunks, top_k=2)

        self.assertEqual(results[0].chunk.text, chunks[0].text)
        self.assertGreater(results[0].sparse_score, results[1].sparse_score)

    def test_auto_scope_selects_one_explicit_version_mention(self) -> None:
        result = resolve_scope(
            "How does PostgreSQL 17 behave?",
            RetrievalFilters(version_mode="auto"),
            {"manual": ("pg16", "pg17")},
        )

        self.assertEqual(result.status, "resolved")
        self.assertEqual(result.filters.product_version, "pg17")

    def test_explicit_latest_and_all_scopes_are_deterministic(self) -> None:
        available = {"a": ("pg16", "pg17"), "b": ("pg15", "pg16")}

        latest = resolve_scope(
            "", RetrievalFilters(version_mode="explicit", version_selector="latest"), available
        )
        all_versions = resolve_scope(
            "", RetrievalFilters(version_mode="explicit", version_selector="all"), available
        )

        self.assertEqual(latest.filters.scopes, (("a", "pg17"), ("b", "pg16")))
        self.assertIsNone(all_versions.filters.scopes)
        self.assertIsNone(all_versions.filters.product_version)


if __name__ == "__main__":
    unittest.main()
