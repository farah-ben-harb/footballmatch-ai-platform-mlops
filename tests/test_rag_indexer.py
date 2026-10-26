"""Tests for automatic RAG analysis indexing."""

from dataclasses import dataclass
from typing import Any

from footballmatch_api.rag.indexer import (
    RagIndexer,
)


@dataclass
class FakeChunk:
    content: str


@dataclass
class FakeDocument:
    job_id: str
    chunks: list[FakeChunk]


class FakeEmbedder:
    def __init__(self) -> None:
        self.received_texts: list[str] = []

    def embed(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        self.received_texts = texts

        return [
            [0.1, 0.2, 0.3]
            for _ in texts
        ]


class FakeRepository:
    def __init__(self) -> None:
        self.document = None
        self.embeddings = None

    def upsert_document(
        self,
        document: Any,
        embeddings: list[list[float]],
    ) -> int:
        self.document = document
        self.embeddings = embeddings

        return 42


def fake_document_builder(
    summary: dict[str, Any],
    *,
    job_id: str,
    mlflow_run_id: str | None,
) -> FakeDocument:
    assert summary == {
        "frames_processed": 100
    }

    assert job_id == "job-123"
    assert (
        mlflow_run_id
        == "run-456"
    )

    return FakeDocument(
        job_id=job_id,
        chunks=[
            FakeChunk(
                content="Tracking information"
            ),
            FakeChunk(
                content="Team classification information"
            ),
        ],
    )


def test_index_analysis() -> None:
    embedder = FakeEmbedder()
    repository = FakeRepository()

    indexer = RagIndexer(
        embedder=embedder,
        repository=repository,
        document_builder=fake_document_builder,
    )

    result = indexer.index_analysis(
        {
            "frames_processed": 100,
        },
        job_id="job-123",
        mlflow_run_id="run-456",
    )

    assert embedder.received_texts == [
        "Tracking information",
        "Team classification information",
    ]

    assert repository.embeddings == [
        [0.1, 0.2, 0.3],
        [0.1, 0.2, 0.3],
    ]

    assert result.document_id == 42
    assert result.job_id == "job-123"
    assert result.chunks_indexed == 2
    assert result.embedding_dimensions == 3


def test_rag_auto_index_disabled_by_default(
    monkeypatch,
) -> None:
    from footballmatch_api.rag.indexer import (
        rag_auto_index_enabled,
    )

    monkeypatch.delenv(
        "FOOTBALLMATCH_RAG_AUTO_INDEX",
        raising=False,
    )

    assert rag_auto_index_enabled() is False


def test_rag_auto_index_enabled(
    monkeypatch,
) -> None:
    from footballmatch_api.rag.indexer import (
        rag_auto_index_enabled,
    )

    monkeypatch.setenv(
        "FOOTBALLMATCH_RAG_AUTO_INDEX",
        "true",
    )

    assert rag_auto_index_enabled() is True


def test_rag_auto_index_accepts_common_true_values(
    monkeypatch,
) -> None:
    from footballmatch_api.rag.indexer import (
        rag_auto_index_enabled,
    )

    for value in (
        "1",
        "TRUE",
        "yes",
        "ON",
    ):
        monkeypatch.setenv(
            "FOOTBALLMATCH_RAG_AUTO_INDEX",
            value,
        )

        assert rag_auto_index_enabled() is True
