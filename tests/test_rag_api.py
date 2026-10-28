"""Tests for the RAG FastAPI endpoints."""

from fastapi import FastAPI
from fastapi.testclient import TestClient

from footballmatch_api.rag.api import (
    get_rag_service,
    router,
)
from footballmatch_api.rag.repository import (
    SearchResult,
)
from footballmatch_api.rag.service import (
    RagAnswer,
)


class FakeRagService:
    """Lightweight fake service: no DB, embeddings, or Ollama."""

    def ask(
        self,
        question: str,
        *,
        limit: int = 3,
    ) -> RagAnswer:
        assert question == (
            "How many player tracks were detected?"
        )
        assert limit == 3

        return RagAnswer(
            answer="18 player tracks were detected.",
            model="fake-model",
            sources=[
                SearchResult(
                    chunk_id=1,
                    document_id=1,
                    job_id="job-123",
                    chunk_index=3,
                    content=(
                        "## Multi-object tracking\n"
                        "Unique tracks by label: person=18"
                    ),
                    metadata={
                        "section": "tracking",
                    },
                    similarity=0.91,
                )
            ],
        )


class FailingRagService:
    """Fake unavailable downstream dependency."""

    def ask(
        self,
        question: str,
        *,
        limit: int = 3,
    ) -> RagAnswer:
        del question, limit

        raise RuntimeError(
            "Ollama unavailable"
        )


def create_test_client(
    service,
) -> TestClient:
    app = FastAPI()

    app.include_router(
        router
    )

    app.dependency_overrides[
        get_rag_service
    ] = lambda: service

    return TestClient(
        app
    )


def test_ask_rag_returns_grounded_answer() -> None:
    client = create_test_client(
        FakeRagService()
    )

    response = client.post(
        "/rag/ask",
        json={
            "question": (
                "How many player tracks "
                "were detected?"
            ),
            "limit": 3,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert (
        data["answer"]
        == "18 player tracks were detected."
    )

    assert data["model"] == "fake-model"

    assert len(
        data["sources"]
    ) == 1

    assert (
        data["sources"][0]["section"]
        == "tracking"
    )

    assert (
        data["sources"][0]["similarity"]
        == 0.91
    )


def test_ask_rag_validates_empty_question() -> None:
    client = create_test_client(
        FakeRagService()
    )

    response = client.post(
        "/rag/ask",
        json={
            "question": "",
            "limit": 3,
        },
    )

    assert response.status_code == 422


def test_ask_rag_validates_limit() -> None:
    client = create_test_client(
        FakeRagService()
    )

    response = client.post(
        "/rag/ask",
        json={
            "question": "test",
            "limit": 10,
        },
    )

    assert response.status_code == 422


def test_ask_rag_returns_503_when_dependency_fails() -> None:
    client = create_test_client(
        FailingRagService()
    )

    response = client.post(
        "/rag/ask",
        json={
            "question": "test",
            "limit": 3,
        },
    )

    assert response.status_code == 503

    assert response.json() == {
        "detail": "Ollama unavailable"
    }


def test_rag_status_does_not_load_service() -> None:
    app = FastAPI()
    app.include_router(router)

    client = TestClient(app)

    response = client.get(
        "/rag/status"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "configured"
    assert data["loading_mode"] == "lazy"
    assert (
        data["embedding_model"]
        == "sentence-transformers/all-MiniLM-L6-v2"
    )
    assert data["ollama_model"] == "gemma3:1b"
    assert data["database"] == "football_rag"
