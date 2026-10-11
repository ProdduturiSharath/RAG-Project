"""Phase 4 host orchestrator: run existing stages, tune on dev, then report test."""

from __future__ import annotations

import asyncio
import json
import os
import random
import time
from pathlib import Path
from typing import Any

import numpy as np

from rag_service.retrieval.encoders import Bm25SparseEncoder, HashEmbeddingEncoder
from rag_service.retrieval.local_models import CrossEncoderReranker, SentenceTransformerEncoder
from rag_service.retrieval.memory import InMemoryHybridIndex
from rag_service.retrieval.models import RetrievalFilters
from rag_service.retrieval.reranking import NoReranker, TokenOverlapReranker
from rag_service.retrieval.service import HybridRetriever, RetrievalConfig

from .experiments import ExperimentConfig, collect_runtime_provenance
from .metrics import covers, guard_nonzero_scores, score_question
from .phase4_config import SystemConfig, systems
from .phase4_data import (
    Snapshot,
    allowed,
    atomic_json,
    chunk_record,
    digest,
    policy_groups,
    preflight,
    rechunk,
)
from .phase4_report import comparisons, summarize, write_failures, write_table

DATABASE_DEFAULT = "postgresql://postgres:postgres@127.0.0.1:5432/evidence_rag_eval"


class Resources:
    def __init__(self, data: dict[str, Any]) -> None:
        self.data = data
        self.snapshots: dict[int, Snapshot] = {}
        self.encoders: dict[tuple[str, bool, bool], Any] = {}
        self.rerankers: dict[str, Any] = {}
        self.qrels: dict[tuple[int, str], tuple[Any, ...]] = {}
        self.records: dict[int, dict[str, dict[str, Any]]] = {}
        self.chunk_maps: dict[int, dict[str, Any]] = {}

    def encoder(self, config: SystemConfig) -> Any:
        key = (config.dense_model, config.query_instruction, config.metadata_prefixed)
        if key not in self.encoders:
            if config.dense_model == "hash-v1":
                encoder: Any = HashEmbeddingEncoder()
            else:
                shared = next((encoder.model for settings, encoder in self.encoders.items()
                               if settings[0] == config.dense_model), None)
                encoder = SentenceTransformerEncoder(
                    config.dense_model, query_instruction=config.query_instruction,
                    metadata_prefixed=config.metadata_prefixed, batch_size=64, model=shared,
                )
            encoder.embed_query("retrieval warmup")
            self.encoders[key] = encoder
        return self.encoders[key]

    def snapshot(self, config: SystemConfig) -> Snapshot:
        tokens = config.chunk_tokens
        if tokens not in self.snapshots:
            chunks = rechunk(self.data["chunks"], tokens)
            provenance = self.data["provenance"]
            key = digest({
                "corpus_sha256": provenance["corpus_sha256"],
                "chunk_counts": provenance["chunk_counts"],
                "policy_sha256": provenance["policy_sha256"],
                "chunk_tokens": tokens,
                "snapshot_format": 2,
            })
            snapshot = Snapshot(self.data["dsn"], key, chunks, self.data["policy"])
            self.snapshots[tokens] = snapshot
            self.records[tokens] = {c.chunk_id: chunk_record(c) for c in chunks}
            self.chunk_maps[tokens] = {c.chunk_id: c for c in chunks}
        return self.snapshots[tokens]

    def relevant(self, config: SystemConfig, row: dict[str, Any]) -> tuple[Any, ...]:
        if not row["evidence_spans"]:
            return ()
        key = (config.chunk_tokens, row["id"])
        if key not in self.qrels:
            self.qrels[key] = tuple(c for c in self.snapshot(config).chunks
                                   if (row["type"] != "acl" or allowed(c, self.data["policy"],
                                                                      row["requester"]))
                                   and covers(row, self.records[config.chunk_tokens][c.chunk_id]))
        return self.qrels[key]

    @staticmethod
    def refresh_metrics(artifact: dict[str, Any], seed: int, samples: int) -> None:
        """Recompute metric definitions from cached rankings without retrieval."""

        for row in artifact["rows"]:
            old_false_exclusion = row.get("metrics", {}).get("false_exclusion")
            row["metrics"] = score_question(
                row, row.get("retrieved", []), row.get("relevant_chunk_count", 0)
            )
            if old_false_exclusion is not None:
                row["metrics"]["false_exclusion"] = old_false_exclusion
        artifact["metrics"] = summarize(artifact["rows"], seed, samples)

    def retriever(self, config: SystemConfig, *, acl: bool) -> HybridRetriever:
        snapshot = self.snapshot(config)
        encoder = self.encoder(config) if config.search_mode != "sparse" else HashEmbeddingEncoder()
        if config.search_mode != "sparse":
            snapshot.ensure_embeddings(config, encoder)
        if config.reranker not in self.rerankers:
            if config.reranker == "none":
                reranker: Any = NoReranker()
            elif config.reranker == "token-overlap":
                reranker = TokenOverlapReranker()
            else:
                from rag_service.domain import Chunk
                from rag_service.retrieval.models import ScoredChunk

                reranker = CrossEncoderReranker()
                reranker.rerank("warmup", [ScoredChunk(Chunk("warmup", "warmup", "v1", "warmup"))])
            self.rerankers[config.reranker] = reranker
        return HybridRetriever(
            snapshot.index(config, acl=acl), encoder, Bm25SparseEncoder(),
            reranker=self.rerankers[config.reranker],
            config=RetrievalConfig(fusion=config.fusion, rerank_top_n=config.rerank_top_n,
                                   version_mode=config.version_mode,
                                   parent_expansion=config.parent_expansion,
                                   search_mode=config.search_mode, persist_traces=False),
        )


def experiment(suite: ExperimentConfig, name: str, system: SystemConfig,
               data: dict[str, Any]) -> ExperimentConfig:
    pipeline = system.model_dump()
    if system.search_mode != "dense" and system.sparse_method == "postgres":
        pipeline["retrieval_revision"] = "postgres-sparse-or-v2"
    if system.version_mode == "auto":
        pipeline["scope_revision"] = "auto-fallback-v2"
    stable_keys = ("corpus_sha256", "embeddings_fingerprint", "gold_sha256",
                   "policy_sha256", "chunk_counts", "gold_rows")
    stable_inputs = {key: data["provenance"][key] for key in stable_keys}
    return ExperimentConfig(
        experiment_id=suite.experiment_id, seed=suite.seed, dataset=suite.dataset, system=name,
        parameters={"pipeline": pipeline, "embedder_id": system.embedder_id,
                    "bootstrap_samples": suite.parameters["bootstrap_samples"],
                    "inputs": stable_inputs},
    )


def _compatible_cached_config(candidate: dict[str, Any], expected: ExperimentConfig) -> bool:
    """Find pre-revision artifacts while keeping the new semantic hash stable."""

    if candidate.get("system") != expected.system:
        return False
    if candidate.get("experiment_id") != expected.experiment_id:
        return False
    if candidate.get("dataset") != expected.dataset or candidate.get("seed") != expected.seed:
        return False
    expected_parameters = expected.model_dump()["parameters"]
    actual_parameters = candidate.get("parameters", {})
    if actual_parameters.get("pipeline") != expected_parameters["pipeline"]:
        return False
    if actual_parameters.get("embedder_id") != expected_parameters["embedder_id"]:
        return False
    return all(actual_parameters.get("inputs", {}).get(key) == value
               for key, value in expected_parameters["inputs"].items())


def _find_cached_artifact(results: Path, expected: ExperimentConfig) -> dict[str, Any] | None:
    for path in sorted(results.glob("*.json")):
        try:
            artifact = json.loads(path.read_text())
        except (OSError, json.JSONDecodeError):
            continue
        if _compatible_cached_config(artifact.get("config", {}), expected):
            return artifact
    return None


async def run_split(config: ExperimentConfig, system: SystemConfig, split: str,
                    resources: Resources,
                    artifact: dict[str, Any], path: Path) -> dict[str, Any]:
    rows = [row for row in resources.data["gold"] if row["split"] == split]
    finished = {row["id"] for row in artifact["rows"]}
    pending = [row for row in rows if row["id"] not in finished]
    if not pending and split in artifact["completed_splits"]:
        Resources.refresh_metrics(artifact, config.seed, config.parameters["bootstrap_samples"])
        guard_nonzero_scores(artifact["rows"], system=config.system)
        atomic_json(path, artifact)
        return artifact
    print(f"{config.system}: {split}, {len(pending)} questions", flush=True)
    setup_start = time.perf_counter()
    retrievers = ({acl: resources.retriever(system, acl=acl) for acl in (False, True)}
                  if pending else {})
    artifact.setdefault("initialization_seconds", []).append(time.perf_counter() - setup_start)
    for number, row in enumerate(pending, 1):
        is_acl = row["type"] == "acl"
        filters = RetrievalFilters(
            principal=row["requester"],
            groups=policy_groups(resources.data["policy"], row["requester"]),
            version_mode=system.version_mode,
            product_version=row["target_version"] if system.version_mode == "explicit" else None,
        )
        started = time.perf_counter()
        result = await retrievers[is_acl].retrieve_detailed(
            row["question"], top_k=system.candidate_k, candidate_k=system.candidate_k,
            alpha=system.alpha, filters=filters,
        )
        elapsed = (time.perf_counter() - started) * 1000
        retrieved = []
        for match in result.matches:
            record = chunk_record(match.chunk)
            record.pop("normalized_text")
            record.update(score=match.final_score, dense_score=match.dense_score,
                          sparse_score=match.sparse_score, rerank_score=match.rerank_score)
            retrieved.append(record)
        if len({c["chunk_id"] for c in retrieved}) != len(retrieved):
            raise ValueError("retrieval returned duplicate chunk IDs")
        relevant = resources.relevant(system, row)
        metrics = score_question(row, retrieved, len(relevant))
        if row["type"] == "unchanged_control" and relevant:
            metrics["false_exclusion"] = float(not any(
                InMemoryHybridIndex._matches(chunk, result.scope.filters) for chunk in relevant
            ))
        exposed = {candidate["chunk_id"] for stage in result.stages
                   for candidate in stage.candidates}
        exposed.update(match.chunk.chunk_id for match in result.matches)
        leakage = sorted(key for key in exposed if is_acl and not allowed(
            resources.chunk_maps[system.chunk_tokens][key],
            resources.data["policy"], row["requester"]
        ))
        first = retrieved[0] if retrieved else None
        record = {
            **row, "metrics": metrics, "retrieved": retrieved,
            "relevant_chunk_count": len(relevant), "leakage_count": len(leakage),
            "leaked_chunk_ids": leakage, "scope_status": result.scope.status,
            "scope_versions": list(result.scope.versions),
            "latency_ms": {**{stage.stage: stage.elapsed_ms for stage in result.stages},
                           "total": elapsed},
            "stages": [{"stage": stage.stage, "details": dict(stage.details),
                        "candidates": list(stage.candidates)} for stage in result.stages],
            "top1_score": first["score"] if first else None,
            "top1_dense_score": first["dense_score"] if first else None,
            "top1_sparse_score": first["sparse_score"] if first else None,
        }
        artifact["rows"].append(record)
        if leakage or number % 25 == 0:
            atomic_json(path, artifact)
        if leakage:
            raise RuntimeError(f"ACL leakage in {config.system}/{row['id']}: "
                               f"{len(leakage)} chunks; "
                               f"diagnostic saved to {path}")
    artifact["rows"].sort(key=lambda row: (row["split"], row["id"]))
    Resources.refresh_metrics(artifact, config.seed, config.parameters["bootstrap_samples"])
    guard_nonzero_scores(artifact["rows"], system=config.system)
    artifact["completed_splits"] = sorted(set(artifact["completed_splits"]) | {split})
    atomic_json(path, artifact)
    return artifact


def dev_score(artifact: dict[str, Any]) -> float:
    value = artifact["metrics"]["dev"]["overall"]["metrics"]["ndcg@10"]["mean"]
    if value is None:
        raise ValueError("cannot select a system without scored dev questions")
    return float(value)


async def run_suite(suite: ExperimentConfig, results: Path, flags: set[str], *,
                    refresh: bool = False,
                    preflight_only: bool = False) -> Path:
    data = preflight(suite, os.environ.get("RAG_EVAL_DATABASE_URL", DATABASE_DEFAULT), results)
    if preflight_only:
        return results / "phase4_preflight.json"
    # Host-only imports and local inference start strictly after preflight.
    import torch

    random.seed(suite.seed)
    np.random.seed(suite.seed)
    torch.manual_seed(suite.seed)
    torch.set_num_threads(int(os.environ.get("RAG_EVAL_THREADS", "4")))
    configs = systems(suite, flags)
    resources = Resources(data)
    artifacts: dict[str, dict[str, Any]] = {}
    experiments = {name: experiment(suite, name, config, data) for name, config in configs.items()}
    parents = {arm["name"]: arm["parent"] for arm in suite.parameters["arms"]}
    for name, exp in experiments.items():
        path = results / f"{exp.config_hash}.json"
        artifact: dict[str, Any] = {
            "config": exp.model_dump(), "config_hash": exp.config_hash, "seed": exp.seed,
            "provenance": {**collect_runtime_provenance(), **data["provenance"]},
            "rows": [], "metrics": {}, "completed_splits": [],
        }
        if path.exists() and not refresh:
            artifact = json.loads(path.read_text())
            if artifact["config"] != exp.model_dump():
                raise ValueError(f"cached config mismatch: {path}")
            expected_ids = {row["id"] for row in data["gold"]}
            cached_ids = [row["id"] for row in artifact["rows"]]
            if len(set(cached_ids)) != len(cached_ids) or not set(cached_ids) <= expected_ids:
                raise ValueError(f"cached question IDs are invalid: {path}")
            if any(row["leakage_count"] for row in artifact["rows"]):
                raise RuntimeError(f"cached result contains ACL leakage: {path}; "
                                   "fix then --refresh")
        elif not refresh:
            cached = _find_cached_artifact(results, exp)
            if cached is not None:
                artifact = cached
                artifact["config"] = exp.model_dump()
                artifact["config_hash"] = exp.config_hash
                provenance: dict[str, Any] = dict(artifact.get("provenance", {}))
                provenance.update(collect_runtime_provenance())
                provenance.update(data["provenance"])
                artifact["provenance"] = provenance
                atomic_json(path, artifact)
        artifacts[name] = await run_split(exp, configs[name], "dev", resources, artifact, path)
    tune_groups: dict[str, list[str]] = {}
    for arm in suite.parameters["arms"]:
        if arm.get("tune"):
            tune_groups.setdefault(str(arm["tune"]), []).append(arm["name"])
    selected_tunes = {
        group: min(names, key=lambda name: (-dev_score(artifacts[name]), name))
        for group, names in tune_groups.items()
    }
    alpha = "; ".join(f"{group}={name}" for group, name in sorted(selected_tunes.items()))
    dev_only = {arm["name"] for arm in suite.parameters["arms"] if arm.get("dev_only")}
    test_names = [name for name in configs if name not in dev_only
                  and (not any(name in names for names in tune_groups.values())
                       or name in selected_tunes.values())]
    best = sorted(test_names, key=lambda name: (-dev_score(artifacts[name]), name))[:2]
    # This decision is persisted BEFORE any test split is evaluated.
    atomic_json(results / "phase4_selection.json", {
        "criterion": "dev ndcg@10 descending, name ascending for ties", "alpha_arm": alpha,
        "tuned_arms": selected_tunes,
        "best_two": best, "dev_scores": {name: dev_score(artifacts[name]) for name in configs},
        "input_fingerprints": data["provenance"],
    })
    print(f"Dev selection frozen: alpha={alpha}, best two={', '.join(best)}", flush=True)
    for name in test_names:
        exp = experiments[name]
        artifacts[name] = await run_split(exp, configs[name], "test", resources, artifacts[name],
                                          results / f"{exp.config_hash}.json")
    for name in best:
        write_failures(name, artifacts[name]["rows"], results)
    differences = comparisons(artifacts, parents, best, suite.seed,
                              suite.parameters["bootstrap_samples"])
    # A real 40-question cache for offline replay/CI, generated only by a host run.
    smoke = [row for row in artifacts["default"]["rows"] if row["split"] == "dev"][:40]
    atomic_json(results / "phase4_smoke.json", {"config_hash": experiments["default"].config_hash,
                                               "rows": smoke})
    scifact = None
    if "scifact" in flags:
        from .scifact import run_scifact

        scifact = await run_scifact(resources, results, refresh=refresh)
    skipped = [arm["name"] for arm in suite.parameters["arms"] if arm.get("flag") not in flags
               and arm.get("flag")]
    if "scifact" not in flags:
        skipped.append("scifact")
    return write_table(artifacts, parents, best, alpha, differences, results, skipped, scifact)


def check_cache(path: Path) -> None:
    cached = json.loads(path.read_text())
    if len(cached["rows"]) != 40:
        raise ValueError("cached smoke gate requires exactly 40 real questions")
    for row in cached["rows"]:
        if row["split"] != "dev" or row["leakage_count"]:
            raise ValueError("cached smoke gate requires dev rows and zero leakage")
        expected = score_question(row, row["retrieved"], row["relevant_chunk_count"])
        if any(row["metrics"][key] != value for key, value in expected.items()):
            raise ValueError(f"cached metric regression: {row['id']}")
    print("Cached 40-question metric/ACL gate passed")


def execute(suite: ExperimentConfig, results: Path, flags: set[str], **kwargs: Any) -> Path:
    return asyncio.run(run_suite(suite, results, flags, **kwargs))
