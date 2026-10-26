"""Ask grounded questions about indexed football analyses."""

import argparse
import os

from footballmatch_api.rag.embedding import (
    SentenceTransformerEmbedder,
)
from footballmatch_api.rag.generator import (
    OllamaGenerator,
)
from footballmatch_api.rag.repository import (
    RagRepository,
)
from footballmatch_api.rag.service import (
    RagService,
)


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "question",
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=3,
    )

    args = parser.parse_args()

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

    generator = OllamaGenerator(
        base_url=os.getenv(
            "FOOTBALLMATCH_OLLAMA_URL",
            "http://host.docker.internal:11434",
        ),
        model=os.getenv(
            "FOOTBALLMATCH_OLLAMA_MODEL",
            "gemma3:1b",
        ),
    )

    service = RagService(
        embedder=embedder,
        repository=repository,
        generator=generator,
    )

    result = service.ask(
        args.question,
        limit=args.limit,
    )

    print()
    print("=== QUESTION ===")
    print(args.question)

    print()
    print("=== ANSWER ===")
    print(result.answer)

    print()
    print("Model:", result.model)

    print()
    print("=== SOURCES ===")

    for index, source in enumerate(
        result.sources,
        start=1,
    ):
        print(
            f"{index}. "
            f"{source.metadata.get('section')} "
            f"(similarity={source.similarity:.4f})"
        )


if __name__ == "__main__":
    main()
