"""FastAPI endpoints for Retrieval Augmented Generation."""

import os
from functools import lru_cache
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from psycopg import OperationalError
from pydantic import BaseModel, Field

from footballmatch_api.rag.embedding import SentenceTransformerEmbedder
from footballmatch_api.rag.generator import OllamaGenerator
from footballmatch_api.rag.repository import RagRepository
from footballmatch_api.rag.service import RagService

router = APIRouter(
    prefix="/rag",
    tags=["rag"],
)


class RagAskRequest(BaseModel):
    """Request payload for a RAG question."""

    question: str = Field(
        min_length=1,
        max_length=500,
    )

    limit: int = Field(
        default=3,
        ge=1,
        le=5,
    )


class RagSourceResponse(BaseModel):
    """Retrieved context used to generate the answer."""

    job_id: str
    section: str | None
    similarity: float
    content: str


class RagAskResponse(BaseModel):
    """Response returned by the RAG API."""

    answer: str
    model: str
    sources: list[RagSourceResponse]


class RagStatusResponse(BaseModel):
    """Configuration status of the RAG subsystem."""

    status: str
    loading_mode: str
    embedding_model: str
    ollama_model: str
    database: str


@lru_cache(maxsize=1)
def get_rag_service() -> RagService:
    """Create and cache the RAG service on first use."""

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

    return RagService(
        embedder=embedder,
        repository=repository,
        generator=generator,
    )


@router.get(
    "/status",
    response_model=RagStatusResponse,
)
def rag_status() -> RagStatusResponse:
    """Return RAG configuration without loading models."""

    return RagStatusResponse(
        status="configured",
        loading_mode="lazy",
        embedding_model=os.getenv(
            "FOOTBALLMATCH_EMBEDDING_MODEL",
            "sentence-transformers/all-MiniLM-L6-v2",
        ),
        ollama_model=os.getenv(
            "FOOTBALLMATCH_OLLAMA_MODEL",
            "gemma3:1b",
        ),
        database=os.getenv(
            "FOOTBALLMATCH_RAG_DB_NAME",
            "football_rag",
        ),
    )


@router.post(
    "/ask",
    response_model=RagAskResponse,
)
def ask_rag(
    request: RagAskRequest,
    service: Annotated[
        RagService,
        Depends(get_rag_service),
    ],
) -> RagAskResponse:
    """Answer a question using RAG."""

    try:
        result = service.ask(
            request.question,
            limit=request.limit,
        )

    except OperationalError as exc:
        raise HTTPException(
            status_code=503,
            detail="RAG database unavailable",
        ) from exc
    except RuntimeError as exc:
        raise HTTPException(
            status_code=503,
            detail=str(exc),
        ) from exc

    sources = [
        RagSourceResponse(
            job_id=source.job_id,
            section=source.metadata.get(
                "section"
            ),
            similarity=source.similarity,
            content=source.content,
        )
        for source in result.sources
    ]

    return RagAskResponse(
        answer=result.answer,
        model=result.model,
        sources=sources,
    )
