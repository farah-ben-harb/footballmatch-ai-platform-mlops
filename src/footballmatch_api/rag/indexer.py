"""Automatic indexing of completed football analyses into the RAG store."""

import os
from collections.abc import Callable
from dataclasses import dataclass
from functools import lru_cache
from typing import Any

from footballmatch_api.rag.document_builder import (
    RagDocument,
    build_analysis_document,
)
from footballmatch_api.rag.embedding import (
    SentenceTransformerEmbedder,
)
from footballmatch_api.rag.repository import (
    RagRepository,
)

DocumentBuilder = Callable[..., RagDocument]


@dataclass(frozen=True)
class RagIndexResult:
    """Result of indexing one completed analysis."""

    document_id: int
    job_id: str
    chunks_indexed: int
    embedding_dimensions: int


class RagIndexer:
    """Build, embed, and persist one analysis document."""

    def __init__(
        self,
        *,
        embedder: Any,
        repository: Any,
        document_builder: DocumentBuilder = build_analysis_document,
    ) -> None:
        self.embedder = embedder
        self.repository = repository
        self.document_builder = document_builder

    def index_analysis(
        self,
        summary: dict[str, Any],
        *,
        job_id: str,
        mlflow_run_id: str | None = None,
    ) -> RagIndexResult:
        """Index one completed analysis in pgvector."""

        document = self.document_builder(
            summary,
            job_id=job_id,
            mlflow_run_id=mlflow_run_id,
        )

        chunk_contents = [
            chunk.content
            for chunk in document.chunks
        ]

        if not chunk_contents:
            raise ValueError(
                "RAG document contains no chunks"
            )

        embeddings = self.embedder.embed(
            chunk_contents
        )

        if len(embeddings) != len(
            document.chunks
        ):
            raise ValueError(
                "Embedding count does not match "
                "the number of RAG chunks"
            )

        document_id = (
            self.repository.upsert_document(
                document,
                embeddings,
            )
        )

        dimensions = (
            len(embeddings[0])
            if embeddings
            else 0
        )

        return RagIndexResult(
            document_id=document_id,
            job_id=document.job_id,
            chunks_indexed=len(
                document.chunks
            ),
            embedding_dimensions=dimensions,
        )


def rag_indexer_from_env() -> RagIndexer:
    """Create the production RAG indexer from environment settings."""

    embedder = SentenceTransformerEmbedder()

    repository = RagRepository(
        host=os.getenv(
            "FOOTBALLMATCH_RAG_DB_HOST",
            "postgres",
        ),
        port=int(
            os.getenv(
                "FOOTBALLMATCH_RAG_DB_PORT",
                "5432",
            )
        ),
        database=os.getenv(
            "FOOTBALLMATCH_RAG_DB_NAME",
            "football_rag",
        ),
        user=os.getenv(
            "FOOTBALLMATCH_RAG_DB_USER",
            "footballmatch",
        ),
        password=os.environ[
            "FOOTBALLMATCH_RAG_DB_PASSWORD"
        ],
    )

    return RagIndexer(
        embedder=embedder,
        repository=repository,
    )



def rag_auto_index_enabled() -> bool:
    """Return whether automatic RAG indexing is enabled."""

    value = os.getenv(
        "FOOTBALLMATCH_RAG_AUTO_INDEX",
        "false",
    )

    return value.strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


@lru_cache(maxsize=1)
def get_rag_indexer() -> RagIndexer:
    """Return one lazily created production RAG indexer."""

    return rag_indexer_from_env()
