"""Semantic search over FootballMatch analysis chunks."""

import argparse
import os

from footballmatch_api.rag.embedding import (
    SentenceTransformerEmbedder,
)
from footballmatch_api.rag.repository import (
    RagRepository,
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
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "query",
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=3,
    )

    args = parser.parse_args()

    embedder = SentenceTransformerEmbedder()

    query_embedding = embedder.embed(
        [args.query]
    )[0]

    repository = repository_from_env()

    results = repository.semantic_search(
        query_embedding,
        limit=args.limit,
    )

    print(
        f"Query: {args.query}"
    )

    print()

    for rank, result in enumerate(
        results,
        start=1,
    ):
        print(
            f"=== RESULT {rank} ==="
        )
        print(
            "Similarity:",
            round(
                result.similarity,
                4,
            ),
        )
        print(
            "Job:",
            result.job_id,
        )
        print(
            "Section:",
            result.metadata.get(
                "section"
            ),
        )
        print(
            result.content
        )
        print()


if __name__ == "__main__":
    main()
