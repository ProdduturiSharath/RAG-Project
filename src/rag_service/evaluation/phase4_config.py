"""Validated one-factor experiment graph, separate from application settings."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from .experiments import ExperimentConfig

MODEL_CARD_URL = "https://huggingface.co/BAAI/bge-small-en-v1.5"
BEIR_SOURCE_URL = "https://github.com/beir-cellar/beir#beers-available-datasets"
SCIFACT_URL = "https://public.ukp.informatik.tu-darmstadt.de/thakur/BEIR/datasets/scifact.zip"
SCIFACT_MD5 = "5f7d1de60b170fc8027bb7898e2efca1"
SCIFACT_PUBLISHED_NDCG10 = 0.71275  # model card: MTEB SciFact test, ndcg_at_10 = 71.275


class SystemConfig(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    dense_model: Literal["bge-small", "bge-base", "hash-v1"] = "bge-small"
    query_instruction: bool = True
    search_mode: Literal["hybrid", "dense", "sparse"] = "hybrid"
    sparse_method: Literal["postgres", "bm25"] = "postgres"
    fusion: Literal["rrf", "weighted"] = "rrf"
    alpha: float = Field(default=0.55, ge=0, le=1)
    reranker: Literal["none", "token-overlap", "cross-encoder"] = "cross-encoder"
    rerank_top_n: int = Field(default=30, ge=1)
    candidate_k: int = Field(default=30, ge=10)
    parent_expansion: bool = True
    metadata_prefixed: bool = False
    version_mode: Literal["none", "explicit", "auto"] = "none"
    chunk_tokens: int = Field(default=220, gt=35)

    @property
    def embedder_id(self) -> str:
        name: str = self.dense_model
        if name != "hash-v1":
            name += "-en-v1.5"
        return name + ("::metadata-v1" if self.metadata_prefixed else "")


def systems(config: ExperimentConfig, flags: set[str]) -> dict[str, SystemConfig]:
    output = {"default": SystemConfig.model_validate(config.parameters["default"])}
    for arm in config.parameters["arms"]:
        if arm.get("flag") and arm["flag"] not in flags:
            continue
        parent = output[arm["parent"]].model_dump()
        child = SystemConfig.model_validate({**parent, **arm["overrides"]})
        changed = [key for key, value in child.model_dump().items() if parent[key] != value]
        if len(changed) != 1 or arm["name"] in output:
            raise ValueError(f"arm must change exactly one setting and have a unique name: {arm}")
        output[arm["name"]] = child
    return output
