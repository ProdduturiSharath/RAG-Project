"""Optional, last-stage BEIR SciFact check using the existing Postgres dense path."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import time
import urllib.request
import zipfile
from pathlib import Path
from typing import Any

from rag_service.domain import Chunk
from rag_service.retrieval.encoders import Bm25SparseEncoder
from rag_service.retrieval.models import RetrievalFilters
from rag_service.retrieval.reranking import NoReranker
from rag_service.retrieval.service import HybridRetriever, RetrievalConfig

from .experiments import ExperimentConfig, collect_runtime_provenance
from .metrics import bootstrap, ndcg
from .phase4_config import (
    BEIR_SOURCE_URL,
    MODEL_CARD_URL,
    SCIFACT_MD5,
    SCIFACT_PUBLISHED_NDCG10,
    SCIFACT_URL,
    SystemConfig,
)
from .phase4_data import Snapshot, atomic_json, digest


async def run_scifact(resources: Any, results: Path, *, refresh: bool = False) -> dict[str, Any]:
    print("SciFact sanity check (last)", flush=True)
    archive_path = results / "cache" / "scifact.zip"
    archive_path.parent.mkdir(parents=True, exist_ok=True)
    if not archive_path.exists():
        temporary = archive_path.with_suffix(".zip.tmp")
        with urllib.request.urlopen(SCIFACT_URL, timeout=120) as response:
            temporary.write_bytes(response.read())
        temporary.replace(archive_path)
    content = archive_path.read_bytes()
    if hashlib.md5(content, usedforsecurity=False).hexdigest() != SCIFACT_MD5:
        raise ValueError(f"SciFact archive does not match official BEIR MD5; remove {archive_path}")
    with zipfile.ZipFile(io.BytesIO(content)) as archive:
        corpus = [json.loads(line) for line in archive.read("scifact/corpus.jsonl").splitlines()]
        query_rows = archive.read("scifact/queries.jsonl").splitlines()
        queries = {str(row["_id"]): row["text"] for row in map(json.loads, query_rows)}
        qrels: dict[str, dict[str, float]] = {}
        reader = csv.DictReader(io.StringIO(archive.read("scifact/qrels/test.tsv").decode()),
                                delimiter="\t")
        for row in reader:
            qrels.setdefault(row["query-id"], {})[row["corpus-id"]] = float(row["score"])
    if len(qrels) != 300 or not corpus or not qrels.keys() <= queries.keys():
        raise ValueError("unexpected SciFact test query/corpus structure")
    config = SystemConfig(search_mode="dense", reranker="none", parent_expansion=False)
    experiment = ExperimentConfig(
        experiment_id="phase-4-scifact", seed=42, dataset=SCIFACT_URL, system="dense-bge-small",
        parameters={"pipeline": config.model_dump(), "archive_md5": SCIFACT_MD5,
                    "code_sha256": resources.data["provenance"]["code_sha256"],
                    "document_format": "title + space + abstract; one document per chunk"},
    )
    path = results / f"{experiment.config_hash}.json"
    if path.exists() and not refresh:
        return json.loads(path.read_text())
    chunks = []
    for row in corpus:
        text = (row.get("title", "") + " " + row["text"]).strip()
        chunks.append(Chunk(chunk_id=str(row["_id"]), document_id="scifact", version="test",
                            text=text, lineage_key=str(row["_id"]),
                            content_hash=hashlib.sha256(text.encode()).hexdigest()))
    snapshot = Snapshot(resources.data["dsn"], digest(experiment.model_dump()), tuple(chunks),
                        resources.data["policy"])
    encoder = resources.encoder(config)
    snapshot.ensure_embeddings(config, encoder)
    retriever = HybridRetriever(snapshot.index(config), encoder, Bm25SparseEncoder(),
                                reranker=NoReranker(), config=RetrievalConfig(
                                    search_mode="dense", parent_expansion=False,
                                    persist_traces=False))
    scores = []
    latency: dict[str, list[float]] = {}
    run = {}
    for query_id in sorted(qrels):
        started = time.perf_counter()
        result = await retriever.retrieve_detailed(queries[query_id], top_k=11, candidate_k=11,
                                                   filters=RetrievalFilters(version_mode="none"))
        latency.setdefault("total", []).append((time.perf_counter() - started) * 1000)
        for stage in result.stages:
            latency.setdefault(stage.stage, []).append(stage.elapsed_ms)
        # BEIR EvaluateRetrieval defaults to ignore_identical_ids=True.
        matches = [match for match in result.matches if match.chunk.chunk_id != query_id][:10]
        grades = [qrels[query_id].get(match.chunk.chunk_id, 0.0) for match in matches]
        scores.append(ndcg(grades, list(qrels[query_id].values())))
        run[query_id] = [{"document_id": match.chunk.chunk_id, "score": match.dense_score}
                         for match in matches]
    interval = bootstrap(scores, sorted(qrels), seed=42)
    artifact = {"config": experiment.model_dump(), "config_hash": experiment.config_hash,
              "ndcg@10": interval["mean"], "ci95": interval["ci95"],
              "published_ndcg@10": SCIFACT_PUBLISHED_NDCG10,
              "dataset_url": SCIFACT_URL, "dataset_list_url": BEIR_SOURCE_URL,
              "model_card_url": MODEL_CARD_URL, "queries": len(qrels), "documents": len(chunks),
              "latency_ms": {stage: bootstrap(values, sorted(qrels))
                             for stage, values in latency.items()},
              "run": run, "provenance": collect_runtime_provenance()}
    atomic_json(path, artifact)
    print(f"SciFact nDCG@10: measured={interval['mean']:.5f}, "
          f"published={SCIFACT_PUBLISHED_NDCG10:.5f}", flush=True)
    return artifact
