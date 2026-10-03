"""Local CPU sentence-transformers adapters; weights are loaded once per instance."""

from collections.abc import Sequence
from dataclasses import replace
from typing import Any

from rag_service.domain import Chunk

from .models import ScoredChunk

BGE_MODELS = {"bge-small": "BAAI/bge-small-en-v1.5", "bge-base": "BAAI/bge-base-en-v1.5"}
QUERY_PREFIX = "Represent this sentence for searching relevant passages: "


def embedding_text(chunk: Chunk, prefixed: bool) -> str:
    if not prefixed:
        return chunk.text
    return (f"Document: {chunk.document_id}\nProduct version: {chunk.version}\n"
            f"Section: {' / '.join(chunk.section_path)}\n\n{chunk.text}")


class SentenceTransformerEncoder:
    def __init__(self, model_name: str = "bge-small", *, batch_size: int = 32,
                 metadata_prefixed: bool = False, model: Any = None) -> None:
        from sentence_transformers import SentenceTransformer

        self.model_name = BGE_MODELS.get(model_name, model_name)
        self.batch_size = batch_size
        self.metadata_prefixed = metadata_prefixed
        self.model = model
        self._model_type = SentenceTransformer
        self.dimensions = self._model_dimensions(model) if model is not None else 0

    def _loaded_model(self) -> Any:
        if self.model is None:
            self.model = self._model_type(self.model_name, device="cpu", trust_remote_code=False)
            self.dimensions = self._model_dimensions(self.model)
        return self.model

    @staticmethod
    def _model_dimensions(model: Any) -> int:
        method = getattr(model, "get_embedding_dimension", None)
        if method is None:
            method = model.get_sentence_embedding_dimension
        return int(method())

    def embed(self, texts: Sequence[str]) -> tuple[tuple[float, ...], ...]:
        if not texts:
            return ()
        values = self._loaded_model().encode(list(texts), batch_size=self.batch_size,
                                   normalize_embeddings=True, show_progress_bar=False)
        return tuple(tuple(float(x) for x in row) for row in values)

    def embed_query(self, query: str) -> tuple[float, ...]:
        return self.embed((QUERY_PREFIX + query,))[0]

    def embed_chunks(self, chunks: Sequence[Chunk]) -> tuple[tuple[float, ...], ...]:
        return self.embed(tuple(
            embedding_text(chunk, self.metadata_prefixed) for chunk in chunks
        ))


class CrossEncoderReranker:
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L6-v2", *,
                 batch_size: int = 32, model: Any = None) -> None:
        from sentence_transformers import CrossEncoder

        self.model = model
        self._model_type = CrossEncoder
        self.model_name = model_name
        self.batch_size = batch_size

    def rerank(self, query: str, candidates: Sequence[ScoredChunk]) -> tuple[ScoredChunk, ...]:
        if not candidates:
            return ()
        if self.model is None:
            self.model = self._model_type(
                self.model_name, device="cpu", trust_remote_code=False
            )
        scores = self.model.predict([(query, c.text) for c in candidates],
                                    batch_size=self.batch_size, show_progress_bar=False)
        results = [replace(c, rerank_score=float(s))
                   for c, s in zip(candidates, scores, strict=True)]
        results.sort(key=lambda c: (-c.final_score, c.chunk.chunk_id))
        return tuple(replace(c, rank=i) for i, c in enumerate(results, 1))
