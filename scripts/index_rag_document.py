"""Embed and index a generated RAG document in pgvector."""

import json
import os
from pathlib import Path
from typing import Any

from footballmatch_api.rag.document_builder import (
    build_analysis_document,
)
from footballmatch_api.rag.embedding import (
    SentenceTransformerEmbedder,
)
from footballmatch_api.rag.repository import (
    RagRepository,
)


def load_payload(
    path: Path,
) -> dict[str, Any]:
    return json.loads(
        path.read_text()
    )


def repository_from_env() -> RagRepository:
    return RagRepository(
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


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "input",
        type=Path,
    )

    args = parser.parse_args()

    payload = load_payload(
        args.input
    )

    summary = payload.get(
        "result",
        payload,
    )

    job_id = str(
        payload.get(
            "id",
            payload.get(
                "job_id",
                "unknown",
            ),
        )
    )

    document = build_analysis_document(
        summary,
        job_id=job_id,
        mlflow_run_id=payload.get(
            "mlflow_run_id"
        ),
    )

    embedder = SentenceTransformerEmbedder()

    embeddings = embedder.embed(
        [
            chunk.content
            for chunk in document.chunks
        ]
    )

    repository = repository_from_env()

    document_id = repository.upsert_document(
        document,
        embeddings,
    )

    print(
        "Indexed document ID:",
        document_id,
    )

    print(
        "Job ID:",
        document.job_id,
    )

    print(
        "Chunks indexed:",
        len(document.chunks),
    )

    print(
        "Embedding dimensions:",
        len(embeddings[0])
        if embeddings
        else 0,
    )


if __name__ == "__main__":
    main()
