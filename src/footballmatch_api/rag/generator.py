"""Grounded answer generation with Ollama."""

import json
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from footballmatch_api.rag.repository import SearchResult


@dataclass(frozen=True)
class GeneratedAnswer:
    """Answer generated from retrieved RAG context."""

    content: str
    model: str


class OllamaGenerator:
    """Generate grounded answers using Ollama."""

    def __init__(
        self,
        *,
        base_url: str,
        model: str = "gemma3:1b",
        timeout_seconds: int = 120,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout_seconds = timeout_seconds

    def generate(
        self,
        question: str,
        contexts: list[SearchResult],
    ) -> GeneratedAnswer:
        """Generate an answer using retrieved context only."""

        context_text = "\n\n".join(
            (
                f"[Context {index}]\n"
                f"Section: "
                f"{result.metadata.get('section', 'unknown')}\n"
                f"Job ID: {result.job_id}\n"
                f"Similarity: {result.similarity:.4f}\n"
                f"{result.content}"
            )
            for index, result in enumerate(
                contexts,
                start=1,
            )
        )

        system_prompt = (
            "You are the FootballMatch AI analysis assistant. "
            "Answer only from the supplied analysis context. "
            "Do not invent statistics, players, teams, events, "
            "or facts. If the context does not contain enough "
            "information, answer: "
            "'The available analysis does not contain enough "
            "information.'"
        )

        user_prompt = (
            "ANALYSIS CONTEXT\n"
            "================\n"
            f"{context_text}\n\n"
            "QUESTION\n"
            "========\n"
            f"{question}\n\n"
            "Answer concisely using only the context."
        )

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
            "stream": False,
            "options": {
                "temperature": 0.1,
            },
        }

        request = Request(
            f"{self.base_url}/api/chat",
            data=json.dumps(
                payload
            ).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with urlopen(
                request,
                timeout=self.timeout_seconds,
            ) as response:
                response_payload = json.loads(
                    response.read().decode("utf-8")
                )
        except HTTPError as exc:
            raise RuntimeError(
                f"Ollama returned HTTP {exc.code}"
            ) from exc
        except URLError as exc:
            raise RuntimeError(
                "Unable to connect to Ollama"
            ) from exc

        message = response_payload.get(
            "message",
            {},
        )

        content = str(
            message.get(
                "content",
                "",
            )
        ).strip()

        if not content:
            raise RuntimeError(
                "Ollama returned an empty answer"
            )

        return GeneratedAnswer(
            content=content,
            model=str(
                response_payload.get(
                    "model",
                    self.model,
                )
            ),
        )
