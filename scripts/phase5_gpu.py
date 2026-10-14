#!/usr/bin/env python3
"""GPU-pod Phase 5 sweep, hard-negative mining, and fine-tuning."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
import random
import re
import subprocess
import sys
import tarfile
import urllib.error
import urllib.request
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
HF_MODELS_URL = "https://huggingface.co/api/models?pipeline_tag=sentence-similarity&library=sentence-transformers&sort=downloads&direction=-1&limit=100"
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
    {
        "model": "intfloat/e5-base-v2",
        "query_prefix": "query: ",
        "passage_prefix": "passage: ",
        "license": "mit",
        "source": "https://huggingface.co/intfloat/e5-base-v2",
    },
    {
        "model": "intfloat/e5-large-v2",
        "query_prefix": "query: ",
        "passage_prefix": "passage: ",
        "license": "mit",
        "source": "https://huggingface.co/intfloat/e5-large-v2",
    },
    {
        "model": "sentence-transformers/all-MiniLM-L12-v2",
        "query_prefix": "",
        "passage_prefix": "",
        "license": "apache-2.0",
        "source": "https://huggingface.co/sentence-transformers/all-MiniLM-L12-v2",
    },
)


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
    """Use the live HF/MTEB catalog, retaining a documented safe fallback."""

    discovered: list[dict[str, Any]] = []
    try:
        with urllib.request.urlopen(HF_MODELS_URL, timeout=30) as response:
            values = json.loads(response.read())
        for item in values:
            model = str(item.get("modelId", ""))
            card = item.get("cardData") or {}
            license_name = str(card.get("license", "")).casefold()
            language = card.get("language", ["en"])
            if isinstance(language, str):
                language = [language]
            if not model or "en" not in {str(value).casefold() for value in language}:
                continue
            if license_name not in {"mit", "apache-2.0", "apache-2.0 license", "bsd-3-clause"}:
                continue
            # The MTEB leaderboard is the quality source; downloads are only
            # used to enumerate current candidates, never as the score.
            if item.get("pipeline_tag") not in {None, "sentence-similarity"}:
                continue
            if model not in {value["model"] for value in FALLBACK_EMBEDDERS}:
                discovered.append(
                    {
                        "model": model,
                        "query_prefix": "",
                        "passage_prefix": "",
                        "license": license_name,
                        "source": f"https://huggingface.co/{model}",
                    }
                )
    except (OSError, ValueError, urllib.error.URLError):
        pass
    ordered: list[dict[str, Any]] = []
    for required in FALLBACK_EMBEDDERS[:2]:
        ordered.append(required)
    for candidate in [*FALLBACK_EMBEDDERS[2:], *discovered]:
        if candidate["model"] not in {item["model"] for item in ordered}:
            ordered.append(candidate)
        if len(ordered) == 5:
            break
    return ordered


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


def mine_hard_negatives(
    passages: list[dict[str, Any]],
    queries: list[dict[str, Any]],
    output: Path,
    manifest: dict[str, Any],
) -> list[dict[str, Any]]:
    from rag_service.domain import Chunk
    from rag_service.retrieval.bm25 import bm25_search
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
        encoder.embed([row["question"] for row in queries]), dtype=np.float32
    )
    vector_by_hash = {
        row["content_hash"]: vector for row, vector in zip(passages, passage_vectors, strict=True)
    }
    result: list[dict[str, Any]] = []
    for query, vector in zip(queries, query_vectors, strict=True):
        positive_hash = str(query["positive_content_hash"])
        positive = by_hash[positive_hash]
        dense_scores = sorted(
            (
                (float(np.dot(vector, candidate)), candidate["content_hash"])
                for candidate in passages
            ),
            key=lambda item: (-item[0], item[1]),
        )
        dense_pool = [
            key
            for _, key in dense_scores[2:30]
            if key in vector_by_hash and hard_negative_allowed(positive, by_hash[key])
        ]
        sparse = bm25_search(str(query["question"]), chunks, 30)
        sparse_pool = [
            match.chunk.content_hash or match.chunk.chunk_id
            for match in sparse[2:30]
            if match.chunk.content_hash
            and hard_negative_allowed(positive, by_hash[match.chunk.content_hash])
        ]
        negatives = list(dict.fromkeys([*dense_pool, *sparse_pool]))
        if not negatives:
            raise RuntimeError(f"no false-negative-safe hard negative for {query['query_id']}")
        result.append(
            {
                "query_id": query["query_id"],
                "question": query["question"],
                "positive_content_hash": positive_hash,
                "negative_content_hashes": negatives,
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
    for row in hard:
        negative = by_hash[row["negative_content_hashes"][0]]
        examples.append(
            {
                "query_id": row["query_id"],
                "question": row["question"],
                "positive_text": by_hash[row["positive_content_hash"]]["text"],
                "negative_text": negative["text"],
            }
        )
    fine_tuned: list[dict[str, Any]] = []
    for base in ("BAAI/bge-small-en-v1.5", "BAAI/bge-base-en-v1.5"):
        for seed in (1, 2, 3):
            checkpoint = train_one(base, seed, examples, output)
            item = embed_finetuned(output, checkpoint, base, seed, corpus, queries, eval_rows)
            fine_tuned.append(item)
            state["training"].append(item)
            atomic_json(state_path, state)
    summary = {
        "phase": "5",
        "generated_at": datetime.now(UTC).isoformat(),
        "versions": versions,
        "mteb_source": MTEB_URL,
        "embedder_sweep": sweep,
        "hard_negative_count": len(hard),
        "hard_negative_ranks": "3-30",
        "training": {
            "models": ["BAAI/bge-small-en-v1.5", "BAAI/bge-base-en-v1.5"],
            "seeds": [1, 2, 3],
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
