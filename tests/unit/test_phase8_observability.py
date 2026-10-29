from __future__ import annotations

import time

import httpx
import jwt

from rag_service.api.app import create_app
from rag_service.application import RagApplication
from rag_service.domain import DocumentSection
from rag_service.generation.extractive import ExtractiveAnswerGenerator
from rag_service.ingestion import DeterministicChunker, IngestionPipeline
from rag_service.retrieval import Bm25SparseEncoder, HashEmbeddingEncoder, InMemoryHybridIndex
from rag_service.retrieval.service import HybridRetriever
from rag_service.settings import Settings


async def test_phase8_query_modes_traces_coverage_and_summary() -> None:
    settings = Settings(
        dense_model="hash-v1",
        reranker_model="token-overlap",
        rate_limit_requests=100,
    )
    index = InMemoryHybridIndex()
    encoder = HashEmbeddingEncoder()
    sparse = Bm25SparseEncoder()
    pipeline = IngestionPipeline(
        DeterministicChunker(max_tokens=40, overlap_tokens=0),
        embedder=encoder,
        sparse_encoder=sparse,
        index_writer=index,
    )
    pipeline.ingest("phase8", [DocumentSection(text="WAL protects committed changes.")], "pg-17")
    application = RagApplication(
        pipeline,
        HybridRetriever(index, encoder, sparse),
        ExtractiveAnswerGenerator(minimum_score=0.0),
        verify_generation=True,
    )
    app = create_app(application, settings)
    now = int(time.time())
    token = jwt.encode(
        {"sub": "demo", "groups": [], "roles": ["reader"], "iat": now, "exp": now + 300},
        settings.jwt_secret,
        algorithm="HS256",
    )
    headers = {"Authorization": f"Bearer {token}"}

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://local"
    ) as client:
        response = await client.post(
            "/v1/query",
            headers=headers,
            json={
                "query": "What does WAL protect?",
                "generation_mode": "extractive",
                "search_mode": "hybrid",
            },
        )
        assert response.status_code == 200
        body = response.json()
        assert body["generation_mode"] == "extractive"
        assert body["trace_id"]

        trace = await client.get(f"/v1/traces/{body['trace_id']}", headers=headers)
        assert trace.status_code == 200
        assert trace.json()["generation_mode"] == "extractive"
        assert trace.json()["cost_usd"] == 0.0

        coverage = await client.get("/v1/corpus/coverage", headers=headers)
        assert coverage.json()["total_active_chunks"] == 1
        assert coverage.json()["missing_dense_chunks"] == 0

        summary = await client.get("/v1/traces/summary", headers=headers)
        assert summary.status_code == 200
        assert summary.json()["traces"] == 1
