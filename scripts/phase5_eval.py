#!/usr/bin/env python3
"""Host-side Phase 5 evaluation over the frozen gold set."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import statistics
import urllib.request
import zipfile
from collections import defaultdict
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import numpy as np
import psycopg
import yaml
from psycopg import sql
from psycopg.rows import dict_row

from rag_service.domain import Chunk
from rag_service.evaluation.metrics import (
    bootstrap,
    covers,
    guard_nonzero_scores,
    paired_bootstrap,
    scope_matches,
    score_question,
)
from rag_service.evaluation.phase4_data import allowed
from rag_service.evaluation.phase5 import normalize
from rag_service.retrieval.bm25 import bm25_search
from rag_service.retrieval.models import RetrievalFilters
from rag_service.retrieval.scope import resolve_scope
from rag_service.storage.serialization import chunk_from_payload

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "phase5_outputs"
DEFAULT_RESULTS = ROOT / "results"
DATABASE_DEFAULT = "postgresql://postgres:postgres@127.0.0.1:5432/evidence_rag_eval"
SCIFACT_URL = "https://public.ukp.informatik.tu-darmstadt.de/thakur/BEIR/datasets/scifact.zip"
SCIFACT_PUBLISHED = 0.71275
ACL_POLICY_PATH = ROOT / "data" / "acl_demo.yaml"
SECTION_FAMILIES_PATH = ROOT / "data" / "eval" / "section_families.json"


def atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8"
    )
    temporary.replace(path)


def load_vectors(
    output: Path, key: str, *, eval_queries: bool = False
) -> tuple[dict[str, np.ndarray], dict[str, Any]]:
    suffix = "-eval-queries" if eval_queries else ""
    base = output / "vectors" / f"{key}{suffix}"
    matrix = np.load(Path(str(base) + ".npy"), mmap_mode="r")
    index = json.loads(Path(str(base) + ".index.json").read_text(encoding="utf-8"))
    ids = [str(value) for value in index["ids"]]
    if len(ids) != len(matrix):
        raise ValueError(f"vector/index length mismatch for {key}")
    return {
        item: np.asarray(vector, dtype=np.float32) for item, vector in zip(ids, matrix, strict=True)
    }, index


def vector_text(value: Any) -> list[float]:
    if isinstance(value, str):
        return [float(item) for item in value.strip("[]() ").split(",") if item.strip()]
    return [float(item) for item in value]


def load_chunks(connection: psycopg.Connection[Any]) -> list[Chunk]:
    rows = connection.execute("""SELECT c.payload FROM public.chunks c
        JOIN public.document_versions v ON v.id=c.document_version_id
        WHERE v.status='active' ORDER BY c.chunk_key""").fetchall()
    return [chunk_from_payload(dict(row["payload"])) for row in rows]


def load_acl_policy(path: Path = ACL_POLICY_PATH) -> dict[str, Any]:
    """Load the same policy used by the Phase 4 ACL evaluation overlay."""

    policy = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(policy, dict):
        raise ValueError(f"ACL policy is not a mapping: {path}")
    required = {
        "principals",
        "restricted_section_titles",
        "restricted_allowed_groups",
    }
    if not required <= policy.keys():
        raise ValueError(f"ACL policy is missing keys: {sorted(required - policy.keys())}")
    return policy


def load_section_families(path: Path = SECTION_FAMILIES_PATH) -> dict[str, str]:
    value = json.loads(path.read_text(encoding="utf-8"))
    lineages = value.get("lineages", {}) if isinstance(value, dict) else {}
    return {
        str(lineage): str(item["family_key"])
        for lineage, item in lineages.items()
        if isinstance(item, dict) and item.get("family_key")
    }


def policy_groups(policy: Mapping[str, Any], requester: str) -> tuple[str, ...]:
    return next(
        (
            tuple(str(group) for group in principal.get("groups", ()))
            for principal in policy["principals"]
            if principal.get("id") == requester
        ),
        (),
    )


def record_is_restricted(record: Mapping[str, Any], policy: Mapping[str, Any]) -> bool:
    section_path = record.get("section_path", ())
    path = section_path if isinstance(section_path, str) else " / ".join(
        str(item) for item in section_path
    )
    return any(
        str(title).casefold() in path.casefold()
        for title in policy["restricted_section_titles"]
    )


def record_allowed(
    record: Mapping[str, Any], policy: Mapping[str, Any], requester: str
) -> bool:
    if not record_is_restricted(record, policy):
        return True
    groups = set(policy_groups(policy, requester))
    allowed_groups = {str(group) for group in policy["restricted_allowed_groups"]}
    return bool(groups & allowed_groups)


def assert_zero_acl_leakage(
    ranked: list[dict[str, Any]], policy: Mapping[str, Any], requester: str
) -> None:
    leaked = [
        str(record["chunk_id"])
        for record in ranked
        if not record_allowed(record, policy, requester)
    ]
    if leaked:
        raise AssertionError(
            f"ACL leakage for {requester}: {len(leaked)} unauthorized chunks {leaked[:5]}"
        )


def load_base_vectors(
    connection: psycopg.Connection[Any], embedder_id: str
) -> dict[str, np.ndarray]:
    rows = connection.execute(
        """SELECT e.content_hash, e.embedding::text AS vector
        FROM public.embeddings e WHERE e.embedder_id=%s""",
        (embedder_id,),
    ).fetchall()
    return {
        str(row["content_hash"]): np.asarray(vector_text(row["vector"]), dtype=np.float32)
        for row in rows
    }


def import_vectors(
    connection: psycopg.Connection[Any], schema: str, key: str, vectors: dict[str, np.ndarray]
) -> None:
    connection.execute(sql.SQL("CREATE SCHEMA IF NOT EXISTS {} ").format(sql.Identifier(schema)))
    connection.execute(
        sql.SQL("""CREATE TABLE IF NOT EXISTS {}.vectors (
        content_hash text NOT NULL, embedder_id text NOT NULL, dimensions integer NOT NULL,
        embedding vector NOT NULL, PRIMARY KEY(content_hash, embedder_id))""").format(
            sql.Identifier(schema)
        )
    )
    with connection.cursor() as cursor:
        cursor.executemany(
            sql.SQL("""INSERT INTO {}.vectors
            (content_hash, embedder_id, dimensions, embedding) VALUES (%s,%s,%s,%s::vector)
            ON CONFLICT (content_hash, embedder_id) DO UPDATE SET embedding=EXCLUDED.embedding,
            dimensions=EXCLUDED.dimensions""").format(sql.Identifier(schema)),
            [
                (content_hash, key, int(vector.shape[0]), json.dumps(vector.tolist()))
                for content_hash, vector in vectors.items()
            ],
        )
    connection.commit()


def chunk_records(
    chunks: list[Chunk], section_families: Mapping[str, str] | None = None
) -> list[dict[str, Any]]:
    section_families = section_families or {}
    return [
        {
            "chunk_id": chunk.chunk_id,
            "document_id": chunk.document_id,
            "text": chunk.text,
            "normalized_text": normalize(chunk.text),
            "version": chunk.version,
            "lineage_key": chunk.lineage_key or "",
            "section_family": section_families.get(
                chunk.lineage_key or "", chunk.lineage_key or ""
            ),
            "content_hash": chunk.content_hash or "",
            "section_id": chunk.section_id or "",
            "section_path": list(chunk.section_path),
            "parent_id": chunk.parent_id or "",
            "parent_text": chunk.parent_text or "",
            "ordinal": chunk.ordinal,
        }
        for chunk in chunks
    ]


def rank_dense(
    query: np.ndarray,
    records: list[dict[str, Any]],
    vectors: dict[str, np.ndarray],
    top_k: int = 30,
) -> list[dict[str, Any]]:
    scored = []
    for record in records:
        vector = vectors.get(record["content_hash"])
        if vector is None:
            vector = vectors.get(hashlib.sha256(record["text"].encode()).hexdigest())
        if vector is not None and len(vector) == len(query):
            scored.append((float(np.dot(query, vector)), record))
    return [
        dict(record, score=score)
        for score, record in sorted(scored, key=lambda value: (-value[0], value[1]["chunk_id"]))[
            :top_k
        ]
    ]


def rank_bm25(
    query: str, chunks: list[Chunk], records: list[dict[str, Any]], top_k: int = 30
) -> list[dict[str, Any]]:
    by_id = {record["chunk_id"]: record for record in records}
    return [
        dict(by_id[match.chunk.chunk_id], score=float(match.sparse_score))
        for match in bm25_search(query, chunks, top_k)
    ]


def rank_hybrid(
    query: str,
    query_vector: np.ndarray,
    chunks: list[Chunk],
    records: list[dict[str, Any]],
    vectors: dict[str, np.ndarray],
    alpha: float,
    recommended: bool = False,
) -> list[dict[str, Any]]:
    dense = rank_dense(query_vector, records, vectors, 200)
    sparse = rank_bm25(query, chunks, records, 200)
    dense_scores = {row["chunk_id"]: max(0.0, row["score"]) for row in dense}
    sparse_scores = {row["chunk_id"]: row["score"] for row in sparse}
    dense_max = max(dense_scores.values(), default=0.0) or 1.0
    sparse_max = max(sparse_scores.values(), default=0.0) or 1.0
    values = []
    for record in records:
        dense_part = dense_scores.get(record["chunk_id"], 0.0) / dense_max
        sparse_part = sparse_scores.get(record["chunk_id"], 0.0) / sparse_max
        score = alpha * dense_part + (1.0 - alpha) * sparse_part
        values.append((score, record))
    return [
        dict(record, score=score)
        for score, record in sorted(
            values, key=lambda value: (-value[0], value[1]["chunk_id"])
        )[:30]
    ]


def resolve_eval_scope(
    query: str, records: list[dict[str, Any]], *, enabled: bool
) -> tuple[list[dict[str, Any]], Any]:
    """Resolve automatic version scope against the authorized candidate set."""

    if not enabled:
        return records, None
    available: dict[str, set[str]] = defaultdict(set)
    for record in records:
        available[str(record["document_id"])].add(str(record["version"]))
    scope = resolve_scope(
        query,
        RetrievalFilters(version_mode="auto"),
        {document: tuple(versions) for document, versions in available.items()},
        "auto",
    )
    return [record for record in records if scope_matches(record, scope.filters)], scope


def evaluate_arm(
    name: str,
    query_vectors: dict[str, np.ndarray] | None,
    corpus_vectors: dict[str, np.ndarray] | None,
    chunks: list[Chunk],
    records: list[dict[str, Any]],
    rows: list[dict[str, Any]],
    alpha: float | None = None,
    recommended: bool = False,
    policy: Mapping[str, Any] | None = None,
) -> list[dict[str, Any]]:
    if policy is None and any(row["type"] == "acl" for row in rows):
        policy = load_acl_policy()
    output = []
    for row in rows:
        authorized_chunks = chunks
        if row["type"] == "acl":
            if policy is None:
                raise ValueError("ACL evaluation requires a loaded policy")
            authorized_chunks = [
                chunk for chunk in chunks if allowed(chunk, policy, row["requester"])
            ]
        authorized_ids = {chunk.chunk_id for chunk in authorized_chunks}
        authorized_records = [record for record in records if record["chunk_id"] in authorized_ids]
        scope_enabled = recommended or name == "recommended" or name.startswith("ft-recommended-")
        scoped_records, scope = resolve_eval_scope(
            row["question"], authorized_records, enabled=scope_enabled
        )
        scoped_ids = {record["chunk_id"] for record in scoped_records}
        ranked_chunks = [chunk for chunk in authorized_chunks if chunk.chunk_id in scoped_ids]
        if name == "bm25":
            ranked = rank_bm25(row["question"], ranked_chunks, scoped_records)
        elif query_vectors is not None and corpus_vectors is not None:
            query = query_vectors.get(row["id"])
            if query is None:
                raise ValueError(f"missing evaluation query vector {name}/{row['id']}")
            if alpha is None:
                ranked = rank_dense(query, scoped_records, corpus_vectors)
            else:
                ranked = rank_hybrid(
                    row["question"],
                    query,
                    ranked_chunks,
                    scoped_records,
                    corpus_vectors,
                    alpha,
                    recommended,
                )
        else:
            raise ValueError(f"arm {name} has no vector inputs")
        relevant = [record for record in authorized_records if covers(row, record)]
        metrics = score_question(
            row,
            ranked,
            len(relevant),
            relevant=relevant,
            scope=scope.filters if scope is not None else RetrievalFilters(),
        )
        if row["type"] == "acl":
            assert policy is not None
            assert_zero_acl_leakage(ranked, policy, row["requester"])
        output.append(
            {
                **row,
                "arm": name,
                "metrics": metrics,
                "retrieved": ranked,
                "relevant_chunk_count": len(relevant),
                "leakage_count": 0,
                "leaked_chunk_ids": [],
                "scope_status": scope.status if scope is not None else "unscoped",
                "scope_versions": list(scope.versions) if scope is not None else [],
            }
        )
    return output


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    metrics = {key for row in rows for key in row["metrics"]}
    result: dict[str, Any] = {"n": len(rows)}
    for metric in sorted(metrics):
        values = [float(row["metrics"][metric]) for row in rows if metric in row["metrics"]]
        intervals = bootstrap(
            values,
            [
                str(row.get("lineage_key", row.get("id", "")))
                for row in rows
                if metric in row["metrics"]
            ],
            seed=42,
            samples=2000,
        )
        result[metric] = {
            **intervals,
            "std": statistics.pstdev(values) if len(values) > 1 else 0.0,
        }
    return result


def seed_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_seed: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        if "seed" in row:
            by_seed[int(row["seed"])].append(row)
    if not by_seed:
        return {}
    per_seed = {str(seed): summarize(values) for seed, values in sorted(by_seed.items())}
    metrics = {metric for summary in per_seed.values() for metric in summary if metric != "n"}
    across: dict[str, Any] = {}
    for metric in sorted(metrics):
        values = [
            per_seed[str(seed)][metric]["mean"]
            for seed in by_seed
            if per_seed[str(seed)].get(metric, {}).get("mean") is not None
        ]
        across[metric] = {
            "mean": statistics.fmean(values) if values else None,
            "std": statistics.pstdev(values) if len(values) > 1 else 0.0,
            "seeds": len(values),
        }
    return {"per_seed": per_seed, "across_seeds": across}


def aggregate_seed_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Average each metric per question before computing cohort statistics."""

    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[str(row["id"])].append(row)
    aggregated: list[dict[str, Any]] = []
    for question_id, values in sorted(grouped.items()):
        first = values[0]
        lineage_keys = {str(value["lineage_key"]) for value in values}
        if len(lineage_keys) != 1:
            raise ValueError(f"fine-tuned seed lineage mismatch for {question_id}")
        metric_names = {metric for value in values for metric in value["metrics"]}
        metrics = {
            metric: statistics.fmean(
                float(value["metrics"][metric])
                for value in values
                if metric in value["metrics"]
            )
            for metric in sorted(metric_names)
        }
        aggregated.append(
            {
                **first,
                "id": question_id,
                "metrics": metrics,
                "seeds": sorted({int(value["seed"]) for value in values if "seed" in value}),
            }
        )
    return aggregated


def breakdown(rows: list[dict[str, Any]]) -> dict[str, Any]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[f"type:{row['type']}"].append(row)
        groups[f"paraphrased:{bool(row.get('paraphrased'))}"].append(row)
    return {key: summarize(value) for key, value in sorted(groups.items())}


def smoke_gate(arms: dict[str, dict[str, Any]], rows: list[dict[str, Any]]) -> None:
    smoke = rows[:3]
    failures = []
    for name, config in arms.items():
        try:
            result = evaluate_arm(
                name,
                config.get("query_vectors"),
                config.get("corpus_vectors"),
                config["chunks"],
                config["records"],
                smoke,
                config.get("alpha"),
                config.get("recommended", False),
            )
            if name != "bm25" and not any(item["retrieved"] for item in result):
                raise RuntimeError("empty ranking")
            print(f"SMOKE PASS {name}", flush=True)
        except Exception as exc:
            failures.append(f"{name}: {type(exc).__name__}: {exc}")
            print(f"SMOKE FAIL {name}: {exc}", flush=True)
    if failures:
        raise RuntimeError("Phase 5 smoke gate failed: " + "; ".join(failures))


def select_alpha(
    config: dict[str, Any], dev_rows: list[dict[str, Any]], *, recommended: bool = False
) -> tuple[float, dict[float, float]]:
    scores = {}
    for alpha in (0.25, 0.5, 0.75):
        result = evaluate_arm(
            config["name"],
            config["query_vectors"],
            config["corpus_vectors"],
            config["chunks"],
            config["records"],
            dev_rows,
            alpha,
            recommended=recommended,
        )
        values = [row["metrics"]["ndcg@10"] for row in result if "ndcg@10" in row["metrics"]]
        scores[alpha] = statistics.fmean(values) if values else 0.0
    selected = max(scores, key=lambda value: (scores[value], -value))
    return selected, scores


def markdown(result: dict[str, Any]) -> str:
    lines = [
        "# Phase 5 results",
        "",
        "Generated only from `results/phase5_results.json`.",
        "",
        (
            "| Arm | Split | nDCG@10 mean | nDCG@10 std | nDCG@10 CI95 | R@1 mean | MRR mean | "
            "Windowed R@5 mean | Windowed R@5 CI95 | Family R@5 mean | Family R@5 CI95 | "
            "Confusion@1 mean |"
        ),
        "| --- | --- | ---: | ---: | --- | ---: | ---: | ---: | --- | ---: | --- | ---: |",
    ]
    for item in result["summaries"]:
        values = item["summary"]
        ndcg = values.get("ndcg@10", {})
        r1 = values.get("recall@1", {})
        mrr = values.get("mrr", {})
        confusion = values.get("version_confusion@1", {})
        windowed = values.get("windowed_recall@5", {})
        family = values.get("section_family_recall@5", {})
        ci95 = ndcg.get("ci95")
        ci_text = f"[{ci95[0]}, {ci95[1]}]" if ci95 is not None else "—"
        windowed_ci = windowed.get("ci95")
        family_ci = family.get("ci95")
        lines.append(
            f"| {item['arm']} | {item['split']} | {ndcg.get('mean', '—')} | "
            f"{ndcg.get('std', '—')} | {ci_text} | {r1.get('mean', '—')} | "
            f"{mrr.get('mean', '—')} | {windowed.get('mean', '—')} | "
            f"{windowed_ci if windowed_ci is not None else '—'} | "
            f"{family.get('mean', '—')} | {family_ci if family_ci is not None else '—'} | "
            f"{confusion.get('mean', '—')} |"
        )
    return "\n".join(lines) + "\n"


def findings(result: dict[str, Any]) -> str:
    best = result.get("selection", {})
    lines = [
        "# Phase 5 findings",
        "",
        "Generated from `results/phase5_results.json`; no metrics are hand-copied.",
        "",
        f"Dev-selected best untrained dense arm: `{best.get('best_untrained_dense', 'none')}`.",
        f"Dev-selected fine-tuned alphas: `{best.get('fine_tuned_alphas', {})}`.",
        "",
        "Windowed recall concatenates top-5 ordinal chunks within a version/lineage; "
        "section-family recall marks a valid-version sibling family hit.",
        "",
    ]
    for comparison in result.get("comparisons", []):
        lines.append(
            f"- {comparison['left']} vs {comparison['right']}: "
            f"paired nDCG@10 Δ={comparison['delta'].get('mean')} "
            f"CI={comparison['delta'].get('ci95')}."
        )
    lines.extend(["", "| Arm | Split | Windowed R@5 (95% CI) | Section-family R@5 (95% CI) |",
                  "| --- | --- | --- | --- |"])
    for item in result.get("summaries", []):
        values = item["summary"]
        windowed = values.get("windowed_recall@5", {})
        family = values.get("section_family_recall@5", {})
        lines.append(
            f"| {item['arm']} | {item['split']} | {windowed.get('mean', '—')} "
            f"({windowed.get('ci95', '—')}) | {family.get('mean', '—')} "
            f"({family.get('ci95', '—')}) |"
        )
    lines.extend(
        [
            "",
            "## Limits",
            "",
            "- Questions are model-written on both sides; lexical overlap can favor BM25.",
            "- The corpus contains the training passages, so this is retrieval "
            "generalization only.",
            "- Gold cohorts are small and confidence intervals are not a substitute "
            "for replication.",
            "- If BM25 remains ahead, this experiment does not claim fine-tuning wins.",
            "- The reported Phase 4 recommended replay uses the same base vectors but "
            "a local weighted-fusion approximation;",
        ]
    )
    lines[-1] += " it is not a fresh Phase 4 rerun."
    return "\n".join(lines) + "\n"


def load_arm(
    output: Path,
    key: str,
    chunks: list[Chunk],
    records: list[dict[str, Any]],
    connection: psycopg.Connection[Any],
    schema: str,
) -> dict[str, Any]:
    corpus_vectors, _ = load_vectors(output, key)
    query_vectors, _ = load_vectors(output, key, eval_queries=True)
    import_vectors(connection, schema, key, corpus_vectors)
    return {
        "name": key,
        "key": key,
        "corpus_vectors": corpus_vectors,
        "query_vectors": query_vectors,
        "chunks": chunks,
        "records": records,
    }


def comparison_rows(
    artifacts: dict[str, dict[str, list[dict[str, Any]]]], selection: dict[str, Any]
) -> list[dict[str, Any]]:
    comparisons = []
    baselines = ("dense-bge-small", "hybrid-bm25-weighted-025", "recommended", "bm25")
    for left in sorted(artifacts):
        if left in baselines or "-seed-" in left:
            continue
        for right in baselines:
            if right not in artifacts:
                continue
            for split in ("dev", "test"):
                a = [row for row in artifacts[left].get(split, []) if row["split"] == split]
                b = [row for row in artifacts[right].get(split, []) if row["split"] == split]
                if not a or not b:
                    continue
                value = paired_bootstrap(a, b, "ndcg@10", seed=42, samples=2000)
                comparisons.append({"left": left, "right": right, "split": split, "delta": value})
    return comparisons


def run(args: argparse.Namespace) -> int:
    output = Path(args.outputs)
    if not output.is_dir():
        raise RuntimeError(
            f"phase5_outputs/ is required; extract phase5_outputs.tar.gz first: {output}"
        )
    summary = json.loads((output / "run_summary.json").read_text(encoding="utf-8"))
    gold = [
        json.loads(line)
        for line in (ROOT / "data" / "eval" / "gold.jsonl").read_text().splitlines()
        if line.strip()
    ]
    section_families = load_section_families()
    for row in gold:
        row["section_family"] = section_families.get(row["lineage_key"], row["lineage_key"])
        for span in row["evidence_spans"]:
            lineage = span.get("lineage_key", row["lineage_key"])
            span["section_family"] = section_families.get(lineage, lineage)
    dsn = os.environ.get("RAG_EVAL_DATABASE_URL", DATABASE_DEFAULT)
    results_dir = Path(args.results)
    with psycopg.connect(dsn, row_factory=dict_row) as connection:
        chunks = load_chunks(connection)
        records = chunk_records(chunks, section_families)
        schema = (
            "phase5_"
            + hashlib.sha256(
                (summary.get("generated_at", "") + str(len(chunks))).encode()
            ).hexdigest()[:20]
        )
        base_vectors = load_base_vectors(connection, "bge-small-en-v1.5")
        import_vectors(connection, schema, "baseline-bge-small", base_vectors)
        contexts: dict[str, dict[str, Any]] = {
            "dense-bge-small": {
                "name": "dense-bge-small",
                "query_vectors": None,
                "corpus_vectors": base_vectors,
                "chunks": chunks,
                "records": records,
            },
            "bm25": {
                "name": "bm25",
                "query_vectors": None,
                "corpus_vectors": None,
                "chunks": chunks,
                "records": records,
            },
        }
        # The baseline query vectors are produced by the GPU stage, but its
        # corpus vectors are intentionally replaced with the exact Postgres
        # Phase 4 vectors for a like-for-like bge-small comparator.
        baseline_queries, _ = load_vectors(output, "baseline-bge-small", eval_queries=True)
        contexts["dense-bge-small"]["query_vectors"] = baseline_queries
        contexts["recommended"] = {
            **contexts["dense-bge-small"],
            "name": "recommended",
            "alpha": 0.25,
            "recommended": True,
        }
        for item in summary.get("embedder_sweep", []):
            key = str(item["key"])
            name = "dense-" + key
            contexts[name] = load_arm(output, key, chunks, records, connection, schema)
            contexts[name]["name"] = name
        for item in summary.get("fine_tuned", []):
            key = str(item["key"])
            base_model = str(item["base_model"])
            if "bge-small" in base_model:
                base = "bge-small"
            elif "bge-base" in base_model:
                base = "bge-base"
            else:
                base = "snowflake-arctic-embed-m-v1.5"
            contexts[f"{base}-seed-{item['seed']}"] = load_arm(
                output, key, chunks, records, connection, schema
            )
            contexts[f"{base}-seed-{item['seed']}"]["name"] = f"{base}-seed-{item['seed']}"
    if len(gold) != 212:
        raise RuntimeError(f"expected 212 gold rows, found {len(gold)}")

    smoke_gate(contexts, gold)
    dev = [row for row in gold if row["split"] == "dev"]
    test = [row for row in gold if row["split"] == "test"]
    selection: dict[str, Any] = {"fine_tuned_alphas": {}}
    # Select an alpha only on dev.  Each seed is tuned independently; test is
    # evaluated once with the frozen alpha.
    fine_seed_groups = {
        "bge-small": (1, 2, 3),
        "bge-base": (1, 2, 3),
        "snowflake-arctic-embed-m-v1.5": (1,),
    }
    for base, seeds in fine_seed_groups.items():
        for seed in seeds:
            name = f"{base}-seed-{seed}"
            if name not in contexts:
                continue
            alpha, scores = select_alpha(
                contexts[name] | {"name": name}, dev, recommended=True
            )
            contexts[name]["selected_alpha"] = alpha
            selection["fine_tuned_alphas"][name] = {"selected": alpha, "dev": scores}
    dense_names = [
        name for name in contexts if name.startswith("dense-") and name != "dense-bge-small"
    ]
    dev_dense_scores: dict[str, float] = {}
    for name in dense_names:
        rows = evaluate_arm(
            name,
            contexts[name]["query_vectors"],
            contexts[name]["corpus_vectors"],
            contexts[name]["chunks"],
            contexts[name]["records"],
            dev,
        )
        dev_dense_scores[name] = statistics.fmean(
            row["metrics"].get("ndcg@10", 0.0) for row in rows
        )
    selection["best_untrained_dense"] = (
        max(dev_dense_scores, key=lambda name: dev_dense_scores[name])
        if dev_dense_scores
        else "dense-bge-small"
    )

    artifacts: dict[str, dict[str, list[dict[str, Any]]]] = defaultdict(dict)
    for name, config in contexts.items():
        if name == "recommended":
            rows_dev = evaluate_arm(
                name,
                config["query_vectors"],
                config["corpus_vectors"],
                config["chunks"],
                config["records"],
                dev,
                alpha=0.25,
                recommended=True,
            )
            rows_test = evaluate_arm(
                name,
                config["query_vectors"],
                config["corpus_vectors"],
                config["chunks"],
                config["records"],
                test,
                alpha=0.25,
                recommended=True,
            )
        elif name == "bm25" or name.startswith("dense-"):
            rows_dev = evaluate_arm(
                name,
                config.get("query_vectors"),
                config.get("corpus_vectors"),
                config["chunks"],
                config["records"],
                dev,
            )
            rows_test = evaluate_arm(
                name,
                config.get("query_vectors"),
                config.get("corpus_vectors"),
                config["chunks"],
                config["records"],
                test,
            )
        elif any(
            name == f"{base}-seed-{seed}"
            for base, seeds in fine_seed_groups.items()
            for seed in seeds
        ):
            rows_dev = evaluate_arm(
                name,
                config["query_vectors"],
                config["corpus_vectors"],
                config["chunks"],
                config["records"],
                dev,
            )
            rows_test = evaluate_arm(
                name,
                config["query_vectors"],
                config["corpus_vectors"],
                config["chunks"],
                config["records"],
                test,
            )
        else:
            alpha = config.get("selected_alpha", 0.5)
            rows_dev = evaluate_arm(
                name,
                config["query_vectors"],
                config["corpus_vectors"],
                config["chunks"],
                config["records"],
                dev,
            )
            rows_test = evaluate_arm(
                name,
                config["query_vectors"],
                config["corpus_vectors"],
                config["chunks"],
                config["records"],
                test,
                alpha=alpha,
            )
        for rows in (rows_dev, rows_test):
            guard_nonzero_scores(rows, system=name)
        artifacts[name] = {"dev": rows_dev, "test": rows_test}

    # Aggregate fine-tuned seeds per question.  Keep the unaggregated rows only
    # for the seed-specific compatibility summary.
    seed_artifacts: dict[str, dict[str, list[dict[str, Any]]]] = {}
    for base, expected_seeds in fine_seed_groups.items():
        seed_numbers = [seed for seed in expected_seeds if f"{base}-seed-{seed}" in artifacts]
        if len(seed_numbers) != len(expected_seeds):
            continue
        seed_artifacts_for_base = [
            artifacts[f"{base}-seed-{seed}"] for seed in seed_numbers
        ]
        for label, mode in (
            (f"ft-dense-{base}", "dense"),
            (f"ft-hybrid-bm25-{base}", "hybrid"),
            (f"ft-recommended-{base}", "recommended"),
        ):
            raw_by_split: dict[str, list[dict[str, Any]]] = {}
            for split in ("dev", "test"):
                merged: list[dict[str, Any]] = []
                for seed, artifact in zip(seed_numbers, seed_artifacts_for_base, strict=True):
                    selected = artifact[split]
                    if mode != "dense":
                        alpha = selection["fine_tuned_alphas"][f"{base}-seed-{seed}"]["selected"]
                        context = contexts[f"{base}-seed-{seed}"]
                        selected = evaluate_arm(
                            label,
                            context["query_vectors"],
                            context["corpus_vectors"],
                            context["chunks"],
                            context["records"],
                            [row for row in (dev if split == "dev" else test)],
                            alpha=alpha,
                            recommended=mode == "recommended",
                        )
                    merged.extend({**row, "seed": seed} for row in selected)
                raw_by_split[split] = merged
            seed_artifacts[label] = raw_by_split
            artifacts[label] = {
                split: aggregate_seed_rows(rows) for split, rows in raw_by_split.items()
            }
    best_name = selection["best_untrained_dense"]
    best_context = contexts[best_name]
    artifacts["hybrid-best-untrained"] = {
        split: evaluate_arm(
            "hybrid-best-untrained",
            best_context["query_vectors"],
            best_context["corpus_vectors"],
            best_context["chunks"],
            best_context["records"],
            dev if split == "dev" else test,
            alpha=0.5,
        )
        for split in ("dev", "test")
    }
    baseline = contexts["dense-bge-small"]
    artifacts["hybrid-bm25-weighted-025"] = {
        split: evaluate_arm(
            "hybrid-bm25-weighted-025",
            baseline["query_vectors"],
            baseline["corpus_vectors"],
            baseline["chunks"],
            baseline["records"],
            dev if split == "dev" else test,
            alpha=0.25,
        )
        for split in ("dev", "test")
    }

    summaries = [
        {
            "arm": name,
            "split": split,
            "summary": summarize(rows),
            "seed_summary": seed_summary(seed_artifacts[name][split])
            if name in seed_artifacts
            else {},
            "breakdown": breakdown(rows),
        }
        for name, values in sorted(artifacts.items())
        for split, rows in values.items()
    ]
    result = {
        "phase": 5,
        "source": "results only",
        "selection": selection,
        "summaries": summaries,
        "comparisons": comparison_rows(artifacts, selection),
        "scifact": run_scifact_check(best_context, output, summary, best_name),
    }
    results_dir.mkdir(parents=True, exist_ok=True)
    result_path = results_dir / "phase5_results.json"
    atomic_json(result_path, result)
    result_for_reports = json.loads(result_path.read_text(encoding="utf-8"))
    (results_dir / "phase5_table.md").write_text(markdown(result_for_reports), encoding="utf-8")
    (ROOT / "docs" / "phase5_findings.md").write_text(
        findings(result_for_reports), encoding="utf-8"
    )
    print(f"Wrote {results_dir / 'phase5_table.md'} and docs/phase5_findings.md", flush=True)
    return 0


def run_scifact_check(
    context: dict[str, Any], output: Path, run_summary: dict[str, Any], selected_name: str
) -> dict[str, Any]:
    """Optional forgetting check using the dev-selected dense model vectors.

    The public BEIR archive is downloaded only at eval time; a failed download
    is recorded as unavailable rather than inventing a score.
    """

    gpu_summary = run_summary.get("scifact")
    if isinstance(gpu_summary, dict):
        models = gpu_summary.get("models", {})
        lookup = selected_name.removeprefix("dense-")
        selected = models.get(lookup) or models.get("baseline-bge-small")
        if isinstance(selected, dict):
            return {"selected_arm": selected_name, **selected}
        return {
            "status": gpu_summary.get("status", "unavailable"),
            "selected_arm": selected_name,
            "reason": gpu_summary.get("reason", "GPU SciFact result was not available"),
        }
    try:
        from sentence_transformers import SentenceTransformer

        from rag_service.evaluation.metrics import ndcg

        with urllib.request.urlopen(SCIFACT_URL, timeout=120) as response:
            content = response.read()
        with zipfile.ZipFile(io.BytesIO(content)) as archive:
            corpus = [
                json.loads(line) for line in archive.read("scifact/corpus.jsonl").splitlines()
            ]
            queries = {
                str(row["_id"]): row["text"]
                for row in map(json.loads, archive.read("scifact/queries.jsonl").splitlines())
            }
            qrels: dict[str, dict[str, float]] = defaultdict(dict)
            reader = csv.DictReader(
                io.StringIO(archive.read("scifact/qrels/test.tsv").decode()), delimiter="\t"
            )
            for row in reader:
                qrels[row["query-id"]][row["corpus-id"]] = float(row["score"])
        model_name = selected_name.removeprefix("dense-")
        model_spec = next(
            (
                item
                for item in run_summary.get("embedder_sweep", [])
                if item.get("key") == model_name
            ),
            None,
        )
        model_id = (
            str(model_spec.get("model", "BAAI/bge-small-en-v1.5"))
            if model_spec
            else "BAAI/bge-small-en-v1.5"
        )
        model = SentenceTransformer(model_id, device="cpu")
        query_prefix = str(model_spec.get("query_prefix", "")) if model_spec else ""
        passage_prefix = str(model_spec.get("passage_prefix", "")) if model_spec else ""
        corpus_ids = [str(row["_id"]) for row in corpus]
        corpus_vectors = model.encode(
            [passage_prefix + str(row["title"]) + " " + str(row["text"]) for row in corpus],
            normalize_embeddings=True,
            convert_to_numpy=True,
            show_progress_bar=False,
        )
        scores = []
        for query_id, _question in qrels.items():
            query_vector = model.encode(
                [query_prefix + queries[query_id]],
                normalize_embeddings=True,
                convert_to_numpy=True,
                show_progress_bar=False,
            )[0]
            order = np.argsort(-(corpus_vectors @ query_vector))[:10]
            grades = [qrels[query_id].get(corpus_ids[index], 0.0) for index in order]
            scores.append(ndcg(grades, list(qrels[query_id].values())))
        value = statistics.fmean(scores)
        return {
            "status": "ok",
            "selected_model": model_id,
            "selected_arm": selected_name,
            "n": len(scores),
            "ndcg@10": value,
            "published_ndcg@10": SCIFACT_PUBLISHED,
            "delta_vs_published": value - SCIFACT_PUBLISHED,
            "dataset_url": SCIFACT_URL,
        }
    except Exception as exc:
        return {
            "status": "unavailable",
            "selected_arm": selected_name,
            "published_ndcg@10": SCIFACT_PUBLISHED,
            "dataset_url": SCIFACT_URL,
            "reason": f"{type(exc).__name__}: {exc}",
        }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--outputs", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--results", default=str(DEFAULT_RESULTS))
    parser.add_argument("--database-url", default=None)
    args = parser.parse_args()
    if args.database_url:
        os.environ["RAG_EVAL_DATABASE_URL"] = args.database_url
    return run(args)


if __name__ == "__main__":
    raise SystemExit(main())
