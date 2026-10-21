#!/usr/bin/env python3
"""GPU-pod Phase 5 sweep, hard-negative mining, and fine-tuning."""

from __future__ import annotations

import argparse
import csv
import gc
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
import time
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
from scripts import phase5_runtime

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


def load_inputs(input_dir: Path) -> tuple[
    list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]],
    list[dict[str, Any]], dict[str, Any], dict[str, str],
]:
    """Fail before downloads/installation if a clone lacks its frozen training inputs."""
    paths = {
        "train_passages": input_dir / "train_passages.jsonl.gz",
        "corpus_texts": input_dir / "corpus_texts.jsonl.gz",
        "train_queries": input_dir / "train_queries.jsonl.gz",
        "gold": ROOT / "data/eval/gold.jsonl",
        "section_families": ROOT / "data/eval/section_families.json",
    }
    missing = [str(path) for path in paths.values() if not path.is_file()]
    if missing:
        raise RuntimeError("Missing Phase 5 inputs: " + ", ".join(missing))
    passages, corpus, queries = (
        read_gzip_jsonl(paths[name]) for name in ("train_passages", "corpus_texts", "train_queries")
    )
    eval_rows = load_jsonl(paths["gold"])
    manifest = json.loads(paths["section_families"].read_text(encoding="utf-8"))
    if not passages or not corpus or not queries:
        raise RuntimeError(
            "phase5_gpu requires nonempty train_passages, corpus_texts, train_queries"
        )
    if len(eval_rows) != 212:
        raise RuntimeError(f"expected 212 gold rows for host evaluation, found {len(eval_rows)}")
    passage_ids = {row["content_hash"] for row in passages}
    corpus_ids = {row["content_hash"] for row in corpus}
    if len(passage_ids) != len(passages) or len(corpus_ids) != len(corpus):
        raise ValueError("duplicate content hashes in materialized inputs")
    if not passage_ids <= corpus_ids:
        raise ValueError("training positives are missing from corpus_texts")
    if len({row["query_id"] for row in queries}) != len(queries):
        raise ValueError("duplicate training query IDs")
    if any(row["positive_content_hash"] not in passage_ids for row in queries):
        raise ValueError("training query references a missing positive passage")
    fingerprints = {
        name: hashlib.sha256(path.read_bytes()).hexdigest() for name, path in paths.items()
    }
    print(
        f"Inputs verified: {len(passages)} passages, {len(corpus)} corpus texts, "
        f"{len(queries)} kept queries, {len(eval_rows)} eval queries (no 4,000-query minimum)",
        flush=True,
    )
    return passages, corpus, queries, eval_rows, manifest, fingerprints


def safe_id(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("_")


def install_deps() -> None:
    """Install the full pinned dependency graph without replacing image-owned torch/CUDA."""
    phase5_runtime.install_deps(PINNED)


def print_versions() -> dict[str, Any]:
    """Verify training imports and report the actual CUDA runtime and package versions."""
    return phase5_runtime.print_versions()


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


def release_cuda() -> None:
    import torch

    gc.collect()
    torch.cuda.empty_cache()


def load_gpu_model(name: str) -> Any:
    from sentence_transformers import SentenceTransformer

    print(f"Loading GPU model {name}", flush=True)
    model = SentenceTransformer(name, device="cuda", trust_remote_code=False)
    # Prefixes are explicit in this pipeline; do not also apply a saved default prompt.
    model.default_prompt_name = None
    return model


def encode(
    model: Any, texts: list[str], prefix: str, batch_size: int = 64, *, label: str = "encoding"
) -> np.ndarray:
    """Report completed batches; reduce only inference batch size on CUDA OOM."""
    import torch

    if batch_size < 1:
        raise ValueError("encoding batch_size must be positive")
    if not texts:
        return np.empty((0, 0), dtype=np.float32)
    started = time.monotonic()
    parts: list[np.ndarray] = []
    done = 0
    print(f"{label}: 0/{len(texts)} texts (batch_size={batch_size})", flush=True)
    while done < len(texts):
        batch = texts[done : done + batch_size]
        try:
            values = model.encode(
                [prefix + text for text in batch],
                batch_size=batch_size,
                normalize_embeddings=True,
                convert_to_numpy=True,
                show_progress_bar=False,
            )
        except torch.cuda.OutOfMemoryError:
            if batch_size == 1:
                raise
            batch_size = max(1, batch_size // 2)
            release_cuda()
            print(f"{label}: CUDA OOM; retrying at batch_size={batch_size}", flush=True)
            continue
        array = np.asarray(values, dtype=np.float32)
        if array.ndim != 2 or len(array) != len(batch) or not np.isfinite(array).all():
            raise ValueError(f"{label}: invalid or non-finite embedding output")
        parts.append(array)
        done += len(batch)
        elapsed = time.monotonic() - started
        eta = elapsed / done * (len(texts) - done)
        print(f"{label}: {done}/{len(texts)} elapsed={elapsed:.1f}s ETA={eta:.1f}s", flush=True)
    return np.concatenate(parts)


def write_vectors(output: Path, name: str, vectors: np.ndarray, ids: list[str]) -> None:
    vector_dir = output / "vectors"
    vector_dir.mkdir(parents=True, exist_ok=True)
    save_array(vector_dir / f"{safe_id(name)}.npy", vectors)
    atomic_json(
        vector_dir / f"{safe_id(name)}.index.json",
        {"ids": ids, "dimensions": int(vectors.shape[1])},
    )


def save_array(path: Path, values: np.ndarray) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("wb") as stream:
        np.save(stream, values)
    temporary.replace(path)


def vectors_complete(output: Path, key: str, *, train_queries: bool = True) -> bool:
    suffixes = ("", "-eval-queries", "-queries") if train_queries else ("", "-eval-queries")
    return all(
        (output / "vectors" / f"{safe_id(key)}{suffix}{extension}").is_file()
        for suffix in suffixes for extension in (".npy", ".index.json")
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
    model = load_gpu_model("BAAI/bge-small-en-v1.5")
    try:
        passage_vectors = encode(
            model, [row["text"] for row in passages], "", label="Mining passage embeddings"
        )
        query_vectors = encode(
            model, [str(row["question"]) for row in queries], QUERY_PREFIX,
            label="Mining query embeddings",
        )
    finally:
        del model
        release_cuda()
    dense_scores = query_vectors @ passage_vectors.T
    sparse_index = Bm25Index(chunks)
    vector_by_hash = {
        row["content_hash"]: vector for row, vector in zip(passages, passage_vectors, strict=True)
    }
    passage_hashes = np.asarray([str(row["content_hash"]) for row in passages], dtype=object)
    result: list[dict[str, Any]] = []
    started = time.monotonic()
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
        if (query_index + 1) % 100 == 0 or query_index + 1 == len(queries):
            print(
                f"Hard-negative ranking: {query_index + 1}/{len(queries)} "
                f"elapsed={time.monotonic() - started:.1f}s", flush=True,
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
    from datasets import Dataset
    from sentence_transformers import (
        SentenceTransformerTrainer,
        SentenceTransformerTrainingArguments,
    )
    from sentence_transformers.losses import MultipleNegativesRankingLoss
    from transformers.trainer_utils import get_last_checkpoint

    target = output / "checkpoints" / safe_id(base_model) / f"seed-{seed}"
    completed = target / "training_complete.json"
    if completed.exists() and (target / "config_sentence_transformers.json").exists():
        print(f"Reusing completed checkpoint {base_model} seed={seed}", flush=True)
        return target
    if not examples:
        raise ValueError("training requires at least one example")
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    model = load_gpu_model(base_model)
    dataset = Dataset.from_dict({
        "anchor": [QUERY_PREFIX + row["question"] for row in examples],
        "positive": [row["positive_text"] for row in examples],
        "negative": [row["negative_text"] for row in examples],
    })
    checkpoint_dir = target / "checkpoints"
    resume = get_last_checkpoint(str(checkpoint_dir)) if checkpoint_dir.is_dir() else None
    # fit() in ST 5.1.1 wraps this Trainer but does not expose seed/report_to.
    # Preserve the fixed recipe, while passing the actual seed and disabling SaaS loggers.
    training_args = SentenceTransformerTrainingArguments(
        output_dir=str(checkpoint_dir),
        num_train_epochs=2,
        per_device_train_batch_size=16,
        learning_rate=2e-5,
        weight_decay=0.01,
        warmup_steps=max(1, int(((len(examples) + 15) // 16) * 2 * 0.10)),
        optim="adamw_torch",
        fp16=True,
        bf16=False,
        seed=seed,
        data_seed=seed,
        eval_strategy="no",
        save_strategy="steps",
        save_steps=50,
        save_total_limit=2,
        logging_steps=10,
        logging_first_step=True,
        disable_tqdm=False,
        report_to="none",
        push_to_hub=False,
    )
    trainer = SentenceTransformerTrainer(
        model=model, args=training_args, train_dataset=dataset,
        loss=MultipleNegativesRankingLoss(model),
    )
    print(
        f"Training {base_model} seed={seed}: {len(examples)} triplets; resume={resume}", flush=True
    )
    try:
        trainer.train(resume_from_checkpoint=resume)
        model.save(str(target))
        atomic_json(completed, {"base_model": base_model, "seed": seed, "examples": len(examples)})
    finally:
        del trainer, model
        release_cuda()
    return target


def checkpoint_digest(path: Path) -> str:
    digest = hashlib.sha256()
    for item in sorted(path.rglob("*")):
        if item.is_file():
            digest.update(str(item.relative_to(path)).encode())
            with item.open("rb") as stream:
                for block in iter(lambda: stream.read(1024 * 1024), b""):
                    digest.update(block)
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
    model = load_gpu_model(str(checkpoint))
    corpus_ids = [str(row["content_hash"]) for row in corpus]
    query_ids, query_texts = materialized_queries(queries)
    corpus_vectors = encode(model, [str(row["text"]) for row in corpus], "", label="FT corpus")
    query_vectors = encode(model, query_texts, QUERY_PREFIX, label="FT training queries")
    key = f"ft-{safe_id(model_name)}-seed-{seed}"
    write_vectors(output, key, corpus_vectors, corpus_ids)
    save_array(output / "vectors" / f"{safe_id(key)}-queries.npy", query_vectors)
    atomic_json(
        output / "vectors" / f"{safe_id(key)}-queries.index.json",
        {"ids": query_ids, "dimensions": int(query_vectors.shape[1])},
    )
    eval_ids = [str(row["id"]) for row in eval_rows]
    eval_vectors = encode(
        model, [str(row["question"]) for row in eval_rows], QUERY_PREFIX, label="FT eval queries"
    )
    del model
    release_cuda()
    save_array(output / "vectors" / f"{safe_id(key)}-eval-queries.npy", eval_vectors)
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
        for number, spec in enumerate(model_specs, 1):
            print(f"SciFact {number}/{len(model_specs)}: {spec['key']}", flush=True)
            model = load_gpu_model(spec.get("checkpoint", spec.get("model", "")))
            try:
                corpus_vectors = encode(
                    model, corpus_texts, spec["passage_prefix"], label="SciFact corpus"
                )
                query_vectors = encode(
                    model, [queries[query_id] for query_id in query_ids], spec["query_prefix"],
                    label="SciFact queries",
                )
            finally:
                del model
                release_cuda()
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
            atomic_json(output / "scifact_progress.json", {"models": results})
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
    temporary = archive.with_name(archive.name + ".tmp")
    files = sorted(path for path in output.rglob("*") if path.is_file())
    print(f"Packaging {len(files)} files into {archive}", flush=True)
    with tarfile.open(temporary, "w:gz", compresslevel=1) as tar:
        for number, path in enumerate(files, 1):
            tar.add(path, arcname=str(Path("phase5_outputs") / path.relative_to(output)))
            if number % 25 == 0 or number == len(files):
                print(f"Packaging: {number}/{len(files)} files", flush=True)
    temporary.replace(archive)
    with archive.open("rb") as stream:
        checksum = hashlib.file_digest(stream, "sha256").hexdigest()
    archive.with_name(archive.name + ".sha256").write_text(
        f"{checksum}  {archive.name}\n", encoding="utf-8"
    )
    print(f"Wrote {archive}", flush=True)


def stop_pod() -> None:
    pod_id = os.environ.get("RUNPOD_POD_ID")
    try:
        stopped = pod_id is not None and bool(pod_id) and subprocess.call(
            ["runpodctl", "stop", "pod", pod_id], timeout=30
        ) == 0
    except (OSError, subprocess.TimeoutExpired):
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
    passages, corpus, queries, eval_rows, manifest, fingerprints = load_inputs(Path(args.input))
    if getattr(args, "check_inputs", False):
        return 0
    install_deps()
    versions = print_versions()
    if getattr(args, "preflight", False):
        print("Runtime/import preflight passed; no model downloads or training started", flush=True)
        return 0
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    state_path = output / "state.json"
    state = (
        json.loads(state_path.read_text()) if state_path.exists() else {"sweep": {}, "training": []}
    )
    if state_path.exists() and state.get("inputs") != fingerprints:
        raise RuntimeError("output input fingerprints differ/missing; use a new --output directory")
    state["inputs"] = fingerprints
    atomic_json(state_path, state)
    embedders = discover_embedders()
    sweep: list[dict[str, Any]] = []
    for number, spec in enumerate(embedders, 1):
        model_name = spec["model"]
        key = safe_id(model_name)
        print(f"Embedder sweep {number}/{len(embedders)}: {model_name}", flush=True)
        if model_name in state["sweep"] and vectors_complete(output, key):
            item = state["sweep"][model_name]
            sweep.append(item)
            continue
        model = load_gpu_model(model_name)
        parameters = sum(parameter.numel() for parameter in model.parameters())
        if parameters > 600_000_000:
            raise RuntimeError(f"{model_name} has {parameters} parameters, over the 600M cap")
        corpus_vectors = encode(
            model, [str(row["text"]) for row in corpus], spec["passage_prefix"],
            label="Sweep corpus",
        )
        query_ids, query_texts = materialized_queries(queries)
        query_vectors = encode(
            model, query_texts, spec["query_prefix"], label="Sweep train queries"
        )
        if corpus_vectors.shape[1] > 1024:
            raise RuntimeError(f"{model_name} exceeds the 1,024-dimensional sweep limit")
        write_vectors(output, key, corpus_vectors, [str(row["content_hash"]) for row in corpus])
        save_array(output / "vectors" / f"{key}-queries.npy", query_vectors)
        atomic_json(
            output / "vectors" / f"{key}-queries.index.json",
            {"ids": query_ids, "dimensions": int(query_vectors.shape[1])},
        )
        eval_vectors = encode(
            model, [str(row["question"]) for row in eval_rows], spec["query_prefix"],
            label="Sweep eval queries",
        )
        del model
        release_cuda()
        save_array(output / "vectors" / f"{key}-eval-queries.npy", eval_vectors)
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
    if not vectors_complete(output, baseline_key, train_queries=False):
        model = load_gpu_model("BAAI/bge-small-en-v1.5")
        baseline_vectors = encode(
            model, [str(row["text"]) for row in corpus], "", label="Baseline corpus"
        )
        baseline_eval = encode(
            model, [str(row["question"]) for row in eval_rows], QUERY_PREFIX,
            label="Baseline eval queries",
        )
        del model
        release_cuda()
        write_vectors(
            output, baseline_key, baseline_vectors, [str(row["content_hash"]) for row in corpus]
        )
        save_array(output / "vectors" / f"{baseline_key}-eval-queries.npy", baseline_eval)
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
                if key and vectors_complete(output, key):
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
        "inputs": fingerprints,
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
    parser.add_argument(
        "--check-inputs", action="store_true", help="validate inputs offline and exit"
    )
    parser.add_argument(
        "--preflight", action="store_true", help="check inputs, install/imports, CUDA"
    )
    stop = parser.add_mutually_exclusive_group()
    stop.add_argument("--no-stop", dest="stop_on_exit", action="store_false",
                      help="leave pod running for artifact retrieval (default)")
    stop.add_argument("--stop-on-exit", action="store_true",
                      help="stop on exit; requires persistent storage and restart to copy")
    parser.set_defaults(stop_on_exit=False)
    args = parser.parse_args()
    try:
        return run(args)
    finally:
        if args.stop_on_exit:
            stop_pod()
        elif not args.check_inputs:
            print(
                "Pod NOT stopped. Download and verify phase5_outputs.tar.gz, then STOP the pod "
                "manually to end GPU billing. On failure, keep logs/checkpoints for diagnosis.",
                flush=True,
            )


if __name__ == "__main__":
    sys.exit(main())
