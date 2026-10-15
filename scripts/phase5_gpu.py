#!/usr/bin/env python3
"""GPU-pod Phase 5 sweep, hard-negative mining, and fine-tuning."""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import io
import json
import os
import random
import re
import subprocess
import sys
import tarfile
import urllib.request
import zipfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np

from rag_service.evaluation.phase5 import (
    hard_negative_allowed,
    load_jsonl,
    normalize,
    record_family,
    text_hash,
)

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "data" / "train"
DEFAULT_OUTPUT = ROOT / "phase5_outputs"
MTEB_URL = "https://huggingface.co/spaces/mteb/leaderboard"
QUERY_PREFIX = "Represent this sentence for searching relevant passages: "
PINNED = (
    "sentence-transformers==5.1.1",
    "transformers==4.56.2",
    "datasets==4.0.0",
    "accelerate==1.10.1",
    "safetensors==0.6.2",
    "rank-bm25==0.2.2",
)
FALLBACK_EMBEDDERS = (
    {
        "model": "Qwen/Qwen3-Embedding-0.6B",
        "query_prefix": (
            "Instruct: Given a web search query, retrieve relevant passages that answer the query\n"
            "Query: "
        ),
        "passage_prefix": "",
        "license": "apache-2.0",
        "source": "https://huggingface.co/Qwen/Qwen3-Embedding-0.6B",
    },
    {
        "model": "Snowflake/snowflake-arctic-embed-l-v2.0",
        "query_prefix": "query: ",
        "passage_prefix": "",
        "license": "apache-2.0",
        "source": "https://huggingface.co/Snowflake/snowflake-arctic-embed-l-v2.0",
    },
    {
        "model": "BAAI/bge-m3",
        "query_prefix": "",
        "passage_prefix": "",
        "license": "mit",
        "source": "https://huggingface.co/BAAI/bge-m3",
    },
    {
        "model": "BAAI/bge-base-en-v1.5",
        "query_prefix": QUERY_PREFIX,
        "passage_prefix": "",
        "license": "mit",
        "source": "https://huggingface.co/BAAI/bge-base-en-v1.5",
    },
    {
        "model": "BAAI/bge-large-en-v1.5",
        "query_prefix": QUERY_PREFIX,
        "passage_prefix": "",
        "license": "mit",
        "source": "https://huggingface.co/BAAI/bge-large-en-v1.5",
    },
)
STATIC_MTEB_LINEUP = FALLBACK_EMBEDDERS
FINE_TUNE_MODELS = (
    "BAAI/bge-small-en-v1.5",
    "BAAI/bge-base-en-v1.5",
    "Snowflake/snowflake-arctic-embed-m-v1.5",
)
FINE_TUNE_SEEDS = (1, 2, 3)
FINE_TUNE_SEEDS_BY_MODEL = {
    "BAAI/bge-small-en-v1.5": (1, 2, 3),
    "BAAI/bge-base-en-v1.5": (1, 2, 3),
    "Snowflake/snowflake-arctic-embed-m-v1.5": (1,),
}


def atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8"
    )
    temporary.replace(path)


def read_gzip_jsonl(path: Path) -> list[dict[str, Any]]:
    with gzip.open(path, "rt", encoding="utf-8") as stream:
        return [json.loads(line) for line in stream if line.strip()]


def safe_id(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("_")


def install_deps() -> None:
    if os.environ.get("PHASE5_SKIP_INSTALL") == "1":
        print("PHASE5_SKIP_INSTALL=1: skipped pinned dependency installation", flush=True)
        return
    # --no-deps is the torch guard: the pod image owns torch/CUDA and pip may
    # not replace it while installing the Python-side training utilities.
    subprocess.run([sys.executable, "-m", "pip", "install", "--no-deps", *PINNED], check=True)


def print_versions() -> dict[str, Any]:
    import torch

    versions = {
        "python": sys.version,
        "torch": torch.__version__,
        "cuda": torch.version.cuda,
        "cuda_available": bool(torch.cuda.is_available()),
    }
    if torch.cuda.is_available():
        versions["gpu"] = torch.cuda.get_device_name(0)
        versions["gpu_capability"] = list(torch.cuda.get_device_capability(0))
    print(json.dumps({"phase": 5, "versions": versions}, sort_keys=True), flush=True)
    if not torch.cuda.is_available():
        raise RuntimeError("phase5_gpu requires a CUDA GPU; no CPU fallback is allowed")
    return versions


def discover_embedders() -> list[dict[str, Any]]:
    """Return the verified five-model lineup without contacting Hugging Face."""

    if len(STATIC_MTEB_LINEUP) != 5 or len({item["model"] for item in STATIC_MTEB_LINEUP}) != 5:
        raise RuntimeError("static MTEB lineup must contain five unique models")
    return [
        {
            **item,
            "mteb_source": MTEB_URL,
            "lineup_status": "static_verified",
        }
        for item in STATIC_MTEB_LINEUP
    ]


def encode(model: Any, texts: list[str], prefix: str, batch_size: int = 64) -> np.ndarray:
    if not texts:
        return np.empty((0, 0), dtype=np.float32)
    values = model.encode(
        [prefix + text for text in texts],
        batch_size=batch_size,
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=True,
    )
    return np.asarray(values, dtype=np.float32)


def write_vectors(output: Path, name: str, vectors: np.ndarray, ids: list[str]) -> None:
    vector_dir = output / "vectors"
    vector_dir.mkdir(parents=True, exist_ok=True)
    np.save(vector_dir / f"{safe_id(name)}.npy", vectors)
    atomic_json(
        vector_dir / f"{safe_id(name)}.index.json",
        {"ids": ids, "dimensions": int(vectors.shape[1])},
    )


def materialized_queries(queries: list[dict[str, Any]]) -> tuple[list[str], list[str]]:
    return ([str(row["query_id"]) for row in queries], [str(row["question"]) for row in queries])


def add_family_keys(passages: list[dict[str, Any]], manifest: dict[str, Any]) -> None:
    for passage in passages:
        passage["family_key"] = record_family(passage, manifest)
        passage["normalized_text"] = normalize(str(passage["text"]))


def interleave_candidates(dense: list[str], sparse: list[str]) -> list[str]:
    """Interleave dense and sparse candidates while preserving each rank order."""

    result: list[str] = []
    seen: set[str] = set()
    for index in range(max(len(dense), len(sparse))):
        for values in (dense, sparse):
            if index >= len(values):
                continue
            value = str(values[index])
            if value not in seen:
                seen.add(value)
                result.append(value)
    return result


def select_negative_hashes(
    dense: list[str], sparse: list[str], *, limit: int = 8
) -> list[str]:
    """Choose deterministic candidates after interleaving both rankers."""

    if limit < 1:
        raise ValueError("negative limit must be positive")
    return interleave_candidates(dense, sparse)[:limit]


def mine_hard_negatives(
    passages: list[dict[str, Any]],
    queries: list[dict[str, Any]],
    output: Path,
    manifest: dict[str, Any],
) -> list[dict[str, Any]]:
    from rag_service.domain import Chunk
    from rag_service.retrieval.bm25 import Bm25Index
    from rag_service.retrieval.local_models import SentenceTransformerEncoder

    path = output / "hard_negatives.jsonl"
    if path.exists():
        return load_jsonl(path)
    add_family_keys(passages, manifest)
    by_hash = {str(row["content_hash"]): row for row in passages}
    chunks = [
        Chunk(
            chunk_id=key,
            document_id="train",
            version="train",
            text=row["text"],
            kind=row.get("kind", "text"),
            content_hash=key,
            lineage_key=row.get("lineage_key"),
        )
        for key, row in by_hash.items()
    ]
    encoder = SentenceTransformerEncoder("bge-small", batch_size=64, query_instruction=True)
    passage_vectors = np.asarray(encoder.embed([row["text"] for row in passages]), dtype=np.float32)
    query_vectors = np.asarray(
        encoder.embed([QUERY_PREFIX + str(row["question"]) for row in queries]), dtype=np.float32
    )
    dense_scores = query_vectors @ passage_vectors.T
    sparse_index = Bm25Index(chunks)
    vector_by_hash = {
        row["content_hash"]: vector for row, vector in zip(passages, passage_vectors, strict=True)
    }
    passage_hashes = np.asarray([str(row["content_hash"]) for row in passages], dtype=object)
    result: list[dict[str, Any]] = []
    for query_index, query in enumerate(queries):
        positive_hash = str(query["positive_content_hash"])
        positive = by_hash.get(positive_hash)
        if positive is None:
            raise ValueError(f"query {query['query_id']} has no train positive passage")
        dense_order = np.lexsort((passage_hashes, -dense_scores[query_index]))
        dense_pool = [
            str(passage_hashes[index])
            for index in dense_order[2:30]
            if str(passage_hashes[index]) in vector_by_hash
            and hard_negative_allowed(positive, by_hash[str(passage_hashes[index])])
        ]
        sparse = sparse_index.search(str(query["question"]), 30)
        sparse_pool = [
            match.chunk.content_hash or match.chunk.chunk_id
            for match in sparse[2:30]
            if match.chunk.content_hash
            and hard_negative_allowed(positive, by_hash[match.chunk.content_hash])
        ]
        negatives = select_negative_hashes(dense_pool, sparse_pool)
        if not negatives:
            raise RuntimeError(f"no false-negative-safe hard negative for {query['query_id']}")
        result.append(
            {
                "query_id": query["query_id"],
                "question": query["question"],
                "positive_content_hash": positive_hash,
                "negative_content_hashes": negatives,
                "selected_negative_content_hash": negatives[0],
                "mine": {"dense": dense_pool, "bm25": sparse_pool, "ranks": "3-30"},
            }
        )
    output.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".jsonl.tmp")
    temporary.write_text(
        "\n".join(json.dumps(row, sort_keys=True) for row in result) + "\n", encoding="utf-8"
    )
    temporary.replace(path)
    return result


def train_one(base_model: str, seed: int, examples: list[dict[str, Any]], output: Path) -> Path:
    import torch
    from sentence_transformers import InputExample, SentenceTransformer, losses
    from torch.utils.data import DataLoader

    target = output / "checkpoints" / safe_id(base_model) / f"seed-{seed}"
    if (target / "config_sentence_transformers.json").exists():
        return target
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    model = SentenceTransformer(base_model, device="cuda")
    train_examples = [
        InputExample(
            texts=[QUERY_PREFIX + row["question"], row["positive_text"], row["negative_text"]]
        )
        for row in examples
    ]
    loader = DataLoader(train_examples, shuffle=True, batch_size=16)
    loss = losses.MultipleNegativesRankingLoss(model)
    warmup = max(1, int(len(loader) * 2 * 0.10))
    model.fit(
        train_objectives=[(loader, loss)],
        epochs=2,
        warmup_steps=warmup,
        optimizer_params={"lr": 2e-5},
        use_amp=True,
        show_progress_bar=True,
        output_path=str(target),
        checkpoint_path=str(target / "checkpoints"),
        checkpoint_save_steps=0,
    )
    model.save(str(target))
    return target


def checkpoint_digest(path: Path) -> str:
    digest = hashlib.sha256()
    for item in sorted(path.rglob("*")):
        if item.is_file():
            digest.update(str(item.relative_to(path)).encode())
            digest.update(item.read_bytes())
    return digest.hexdigest()


def embed_finetuned(
    output: Path,
    checkpoint: Path,
    model_name: str,
    seed: int,
    corpus: list[dict[str, Any]],
    queries: list[dict[str, Any]],
    eval_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer(str(checkpoint), device="cuda")
    corpus_ids = [str(row["content_hash"]) for row in corpus]
    query_ids, query_texts = materialized_queries(queries)
    corpus_vectors = encode(model, [str(row["text"]) for row in corpus], "")
    query_vectors = encode(model, query_texts, QUERY_PREFIX)
    key = f"ft-{safe_id(model_name)}-seed-{seed}"
    write_vectors(output, key, corpus_vectors, corpus_ids)
    np.save(output / "vectors" / f"{safe_id(key)}-queries.npy", query_vectors)
    atomic_json(
        output / "vectors" / f"{safe_id(key)}-queries.index.json",
        {"ids": query_ids, "dimensions": int(query_vectors.shape[1])},
    )
    eval_ids = [str(row["id"]) for row in eval_rows]
    eval_vectors = encode(model, [str(row["question"]) for row in eval_rows], QUERY_PREFIX)
    np.save(output / "vectors" / f"{safe_id(key)}-eval-queries.npy", eval_vectors)
    atomic_json(
        output / "vectors" / f"{safe_id(key)}-eval-queries.index.json",
        {"ids": eval_ids, "dimensions": int(eval_vectors.shape[1])},
    )
    return {
        "key": key,
        "base_model": model_name,
        "seed": seed,
        "checkpoint": str(checkpoint.relative_to(output)),
        "checkpoint_sha256": checkpoint_digest(checkpoint),
        "dimensions": int(corpus_vectors.shape[1]),
    }


def optional_scifact_summary(output: Path) -> dict[str, Any]:
    """Load a cached SciFact result without downloading or running evaluation."""

    for name in ("scifact_summary.json", "scifact.json"):
        path = output / name
        if not path.exists():
            continue
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            return {"status": "unavailable", "reason": f"{type(exc).__name__}: {exc}"}
        if isinstance(value, dict):
            return {"status": "cached", **value}
        return {"status": "unavailable", "reason": "cached SciFact summary is not an object"}
    return {"status": "not_run", "reason": "optional cached SciFact summary was not supplied"}


def run_scifact_gpu(
    output: Path, sweep: list[dict[str, Any]], fine_tuned: list[dict[str, Any]]
) -> dict[str, Any]:
    """Run the forgetting check on the GPU while the trained models are resident."""

    try:
        from sentence_transformers import SentenceTransformer

        from rag_service.evaluation.metrics import ndcg

        with urllib.request.urlopen(
            "https://public.ukp.informatik.tu-darmstadt.de/thakur/BEIR/datasets/scifact.zip",
            timeout=120,
        ) as response:
            content = response.read()
        with zipfile.ZipFile(io.BytesIO(content)) as archive:
            corpus = [
                json.loads(line) for line in archive.read("scifact/corpus.jsonl").splitlines()
            ]
            queries = {
                str(row["_id"]): str(row["text"])
                for row in map(json.loads, archive.read("scifact/queries.jsonl").splitlines())
            }
            qrels: dict[str, dict[str, float]] = {}
            reader = csv.DictReader(
                io.StringIO(archive.read("scifact/qrels/test.tsv").decode()), delimiter="\t"
            )
            for row in reader:
                qrels.setdefault(row["query-id"], {})[row["corpus-id"]] = float(row["score"])

        model_specs: list[dict[str, Any]] = [
            {
                "key": "baseline-bge-small",
                "model": "BAAI/bge-small-en-v1.5",
                "query_prefix": QUERY_PREFIX,
                "passage_prefix": "",
            }
        ]
        model_specs.extend(
            {
                "key": str(item["key"]),
                "model": str(item["model"]),
                "query_prefix": str(item.get("query_prefix", "")),
                "passage_prefix": str(item.get("passage_prefix", "")),
            }
            for item in sweep
        )
        model_specs.extend(
            {
                "key": str(item["key"]),
                "checkpoint": str(output / str(item["checkpoint"])),
                "query_prefix": QUERY_PREFIX,
                "passage_prefix": "",
            }
            for item in fine_tuned
        )
        results: dict[str, Any] = {}
        corpus_ids = [str(row["_id"]) for row in corpus]
        corpus_texts = [str(row.get("title", "")) + " " + str(row["text"]) for row in corpus]
        query_ids = list(qrels)
        for spec in model_specs:
            model = SentenceTransformer(
                spec.get("checkpoint", spec.get("model", "")), device="cuda"
            )
            corpus_vectors = np.asarray(
                model.encode(
                    [spec["passage_prefix"] + text for text in corpus_texts],
                    batch_size=128,
                    normalize_embeddings=True,
                    convert_to_numpy=True,
                    show_progress_bar=False,
                ),
                dtype=np.float32,
            )
            query_vectors = np.asarray(
                model.encode(
                    [spec["query_prefix"] + queries[query_id] for query_id in query_ids],
                    batch_size=128,
                    normalize_embeddings=True,
                    convert_to_numpy=True,
                    show_progress_bar=False,
                ),
                dtype=np.float32,
            )
            values = []
            for query_id, query_vector in zip(query_ids, query_vectors, strict=True):
                order = np.argsort(-(corpus_vectors @ query_vector))[:10]
                grades = [qrels[query_id].get(corpus_ids[index], 0.0) for index in order]
                values.append(ndcg(grades, list(qrels[query_id].values())))
            results[spec["key"]] = {
                "status": "ok",
                "n": len(values),
                "ndcg@10": float(np.mean(values)) if values else 0.0,
                "published_ndcg@10": 0.71275,
                "delta_vs_published": float(np.mean(values)) - 0.71275 if values else -0.71275,
            }
        return {"status": "ok", "models": results, "dataset_url": "https://public.ukp.informatik.tu-darmstadt.de/thakur/BEIR/datasets/scifact.zip"}
    except Exception as exc:
        return {
            "status": "unavailable",
            "reason": f"{type(exc).__name__}: {exc}",
            "models": {},
        }


def package(output: Path, summary: dict[str, Any]) -> None:
    atomic_json(output / "run_summary.json", summary)
    archive = ROOT / "phase5_outputs.tar.gz"
    temporary = archive.with_suffix(".tar.gz.tmp")
    with tarfile.open(temporary, "w:gz") as tar:
        tar.add(output, arcname="phase5_outputs")
    temporary.replace(archive)
    print(f"Wrote {archive}", flush=True)


def stop_pod() -> None:
    pod_id = os.environ.get("RUNPOD_POD_ID")
    try:
        stopped = bool(pod_id) and subprocess.call(["runpodctl", "stop", "pod", pod_id]) == 0
    except OSError:
        stopped = False
    if stopped:
        print(f"Stopped RunPod pod {pod_id}", flush=True)
        return
    print(
        "!!!!!!!!!!!!!!!! STOP THE POD MANUALLY: "
        "RUNPOD_POD_ID/runpodctl unavailable !!!!!!!!!!!!!!!!",
        flush=True,
    )


def run(args: argparse.Namespace) -> int:
    install_deps()
    versions = print_versions()
    input_dir = Path(args.input)
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    state_path = output / "state.json"
    state = (
        json.loads(state_path.read_text()) if state_path.exists() else {"sweep": {}, "training": []}
    )
    passages = read_gzip_jsonl(input_dir / "train_passages.jsonl.gz")
    corpus = read_gzip_jsonl(input_dir / "corpus_texts.jsonl.gz")
    queries = read_gzip_jsonl(input_dir / "train_queries.jsonl.gz")
    eval_rows = load_jsonl(ROOT / "data" / "eval" / "gold.jsonl")
    manifest = json.loads((ROOT / "data" / "eval" / "section_families.json").read_text())
    if not passages or not corpus or not queries:
        raise RuntimeError("phase5_gpu requires train_passages, corpus_texts, and train_queries")
    embedders = discover_embedders()
    sweep: list[dict[str, Any]] = []
    for spec in embedders:
        model_name = spec["model"]
        key = safe_id(model_name)
        vector_path = output / "vectors" / f"{key}.npy"
        if (
            vector_path.exists()
            and (output / "vectors" / f"{key}-queries.npy").exists()
            and (output / "vectors" / f"{key}-eval-queries.npy").exists()
        ):
            item = state["sweep"].get(model_name, {"model": model_name, "key": key})
            sweep.append(item)
            continue
        from sentence_transformers import SentenceTransformer

        model = SentenceTransformer(model_name, device="cuda")
        parameters = sum(parameter.numel() for parameter in model.parameters())
        if parameters > 600_000_000:
            raise RuntimeError(f"{model_name} has {parameters} parameters, over the 600M cap")
        corpus_vectors = encode(model, [str(row["text"]) for row in corpus], spec["passage_prefix"])
        query_ids, query_texts = materialized_queries(queries)
        query_vectors = encode(model, query_texts, spec["query_prefix"])
        if corpus_vectors.shape[1] > 1024:
            raise RuntimeError(f"{model_name} exceeds the 1,024-dimensional sweep limit")
        write_vectors(output, key, corpus_vectors, [str(row["content_hash"]) for row in corpus])
        np.save(output / "vectors" / f"{key}-queries.npy", query_vectors)
        atomic_json(
            output / "vectors" / f"{key}-queries.index.json",
            {"ids": query_ids, "dimensions": int(query_vectors.shape[1])},
        )
        eval_vectors = encode(
            model, [str(row["question"]) for row in eval_rows], spec["query_prefix"]
        )
        np.save(output / "vectors" / f"{key}-eval-queries.npy", eval_vectors)
        atomic_json(
            output / "vectors" / f"{key}-eval-queries.index.json",
            {
                "ids": [str(row["id"]) for row in eval_rows],
                "dimensions": int(eval_vectors.shape[1]),
            },
        )
        item = {
            "model": model_name,
            "key": key,
            "dimensions": int(corpus_vectors.shape[1]),
            "parameters": parameters,
            "query_prefix": spec["query_prefix"],
            "passage_prefix": spec["passage_prefix"],
            "license": spec["license"],
            "source": spec["source"],
            "mteb_source": MTEB_URL,
        }
        state["sweep"][model_name] = item
        atomic_json(state_path, state)
        sweep.append(item)
    # Keep the Phase 4 bge-small comparison reproducible without relying on
    # whichever local model cache happens to exist on the host.
    baseline_key = "baseline-bge-small"
    if not (output / "vectors" / f"{baseline_key}.npy").exists():
        from sentence_transformers import SentenceTransformer

        model = SentenceTransformer("BAAI/bge-small-en-v1.5", device="cuda")
        baseline_vectors = encode(model, [str(row["text"]) for row in corpus], "")
        baseline_eval = encode(model, [str(row["question"]) for row in eval_rows], QUERY_PREFIX)
        write_vectors(
            output, baseline_key, baseline_vectors, [str(row["content_hash"]) for row in corpus]
        )
        np.save(output / "vectors" / f"{baseline_key}-eval-queries.npy", baseline_eval)
        atomic_json(
            output / "vectors" / f"{baseline_key}-eval-queries.index.json",
            {
                "ids": [str(row["id"]) for row in eval_rows],
                "dimensions": int(baseline_eval.shape[1]),
            },
        )
    hard = mine_hard_negatives(passages, queries, output, manifest)
    by_hash = {str(row["content_hash"]): row for row in passages}
    examples = []
    for index, row in enumerate(hard):
        negative_hashes = row["negative_content_hashes"]
        negative = by_hash[negative_hashes[index % min(4, len(negative_hashes))]]
        examples.append(
            {
                "query_id": row["query_id"],
                "question": row["question"],
                "positive_text": by_hash[row["positive_content_hash"]]["text"],
                "negative_text": negative["text"],
            }
        )
    fine_tuned: list[dict[str, Any]] = []
    training_state = {
        (str(item.get("base_model")), int(item.get("seed", 0))): item
        for item in state.get("training", [])
        if isinstance(item, dict) and item.get("base_model") is not None
    }
    for base in FINE_TUNE_MODELS:
        for seed in FINE_TUNE_SEEDS_BY_MODEL[base]:
            existing = training_state.get((base, seed))
            if existing is not None:
                key = str(existing.get("key", ""))
                required = (
                    output / "vectors" / f"{safe_id(key)}.npy",
                    output / "vectors" / f"{safe_id(key)}-queries.npy",
                    output / "vectors" / f"{safe_id(key)}-eval-queries.npy",
                )
                if key and all(path.exists() for path in required):
                    fine_tuned.append(existing)
                    continue
            checkpoint = train_one(base, seed, examples, output)
            item = embed_finetuned(output, checkpoint, base, seed, corpus, queries, eval_rows)
            fine_tuned.append(item)
            training_state[(base, seed)] = item
            state["training"] = list(training_state.values())
            atomic_json(state_path, state)
    scifact = run_scifact_gpu(output, sweep, fine_tuned)
    if scifact.get("status") == "unavailable":
        cached = optional_scifact_summary(output)
        if cached.get("status") == "cached":
            scifact = cached
    summary = {
        "phase": "5",
        "generated_at": datetime.now(UTC).isoformat(),
        "versions": versions,
        "mteb_source": MTEB_URL,
        "embedder_sweep": sweep,
        "hard_negative_count": len(hard),
        "hard_negative_ranks": "3-30",
        "training": {
            "models": list(FINE_TUNE_MODELS),
            "seeds": {model: list(seeds) for model, seeds in FINE_TUNE_SEEDS_BY_MODEL.items()},
            "loss": "MultipleNegativesRankingLoss",
            "learning_rate": 2e-5,
            "warmup_ratio": 0.10,
            "epochs": 2,
            "fp16": True,
        },
        "fine_tuned": fine_tuned,
        "corpus_texts": len(corpus),
        "train_queries": len(queries),
        "corpus_sha256": text_hash("\n".join(row["content_hash"] for row in corpus)),
        "scifact": scifact,
    }
    package(output, summary)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default=str(DEFAULT_INPUT))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    args = parser.parse_args()
    try:
        return run(args)
    finally:
        stop_pod()


if __name__ == "__main__":
    sys.exit(main())
