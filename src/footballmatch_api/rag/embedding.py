"""Text embeddings used by the FootballMatch RAG pipeline."""

from typing import Any


class SentenceTransformerEmbedder:
    """Generate normalized 384-dimensional text embeddings."""

    def __init__(
        self,
        model_name: str = (
            "sentence-transformers/"
            "all-MiniLM-L6-v2"
        ),
    ) -> None:
        from sentence_transformers import (
            SentenceTransformer,
        )

        self.model_name = model_name
        self._model: Any = SentenceTransformer(
            model_name,
            device="cpu",
        )

    def embed(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        """Embed text and return normalized vectors."""

        if not texts:
            return []

        vectors = self._model.encode(
            texts,
            normalize_embeddings=True,
            show_progress_bar=False,
        )

        result = [
            [
                float(value)
                for value in vector
            ]
            for vector in vectors
        ]

        for vector in result:
            if len(vector) != 384:
                raise ValueError(
                    "Expected 384-dimensional "
                    f"embedding, got {len(vector)}"
                )

        return result
