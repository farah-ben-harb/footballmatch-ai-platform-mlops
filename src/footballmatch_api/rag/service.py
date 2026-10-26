"""End-to-end Retrieval Augmented Generation service."""

from dataclasses import dataclass
from time import perf_counter
from typing import Any

from footballmatch_api.rag.generator import (
    GeneratedAnswer,
    OllamaGenerator,
)
from footballmatch_api.rag.metrics import (
    RAG_ERRORS_TOTAL,
    RAG_GENERATION_SECONDS,
    RAG_REQUESTS_TOTAL,
    RAG_RETRIEVAL_SECONDS,
    RAG_TOTAL_SECONDS,
)
from footballmatch_api.rag.repository import (
    RagRepository,
    SearchResult,
)


@dataclass(frozen=True)
class RagAnswer:
    """Grounded answer and retrieved evidence."""

    answer: str
    model: str
    sources: list[SearchResult]


class RagService:
    """Retrieve semantic context and generate an answer."""

    def __init__(
        self,
        *,
        embedder: Any,
        repository: RagRepository,
        generator: OllamaGenerator,
    ) -> None:
        self.embedder = embedder
        self.repository = repository
        self.generator = generator

    def ask(
        self,
        question: str,
        *,
        limit: int = 3,
    ) -> RagAnswer:
        """Answer a question using retrieval and generation."""

        question = question.strip()

        if not question:
            raise ValueError(
                "question must not be empty"
            )

        RAG_REQUESTS_TOTAL.inc()

        total_started_at = perf_counter()

        try:
            retrieval_started_at = perf_counter()

            try:
                query_embedding = self.embedder.embed(
                    [question]
                )[0]

                sources = (
                    self.repository.semantic_search(
                        query_embedding,
                        limit=limit,
                    )
                )
            finally:
                RAG_RETRIEVAL_SECONDS.observe(
                    perf_counter()
                    - retrieval_started_at
                )

            if not sources:
                return RagAnswer(
                    answer=(
                        "The available analysis does not "
                        "contain enough information."
                    ),
                    model="none",
                    sources=[],
                )

            generation_started_at = perf_counter()

            try:
                generated: GeneratedAnswer = (
                    self.generator.generate(
                        question,
                        sources,
                    )
                )
            finally:
                RAG_GENERATION_SECONDS.observe(
                    perf_counter()
                    - generation_started_at
                )

            return RagAnswer(
                answer=generated.content,
                model=generated.model,
                sources=sources,
            )

        except Exception:
            RAG_ERRORS_TOTAL.inc()
            raise

        finally:
            RAG_TOTAL_SECONDS.observe(
                perf_counter()
                - total_started_at
            )
