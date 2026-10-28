"""PostgreSQL/pgvector persistence for RAG documents."""

import json
from dataclasses import dataclass
from typing import Any

from footballmatch_api.rag.document_builder import (
    RagDocument,
)


@dataclass(frozen=True)
class SearchResult:
    """Semantic-search result."""

    chunk_id: int
    document_id: int
    job_id: str
    chunk_index: int
    content: str
    metadata: dict[str, Any]
    similarity: float


def vector_literal(
    vector: list[float],
) -> str:
    """Convert a Python vector into pgvector literal syntax."""

    return (
        "["
        + ",".join(
            str(float(value))
            for value in vector
        )
        + "]"
    )


class RagRepository:
    """Store and retrieve RAG data using PostgreSQL + pgvector."""

    def __init__(
        self,
        *,
        host: str,
        port: int,
        database: str,
        user: str,
        password: str,
    ) -> None:
        self.connection_parameters = {
            "host": host,
            "port": port,
            "dbname": database,
            "user": user,
            "password": password,
        }

    def _connect(self):
        import psycopg

        return psycopg.connect(
            **self.connection_parameters
        )

    def upsert_document(
        self,
        document: RagDocument,
        embeddings: list[list[float]],
    ) -> int:
        """Insert/update a document and replace its chunks."""

        if len(embeddings) != len(
            document.chunks
        ):
            raise ValueError(
                "Embedding count must match "
                "chunk count"
            )

        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO rag_documents (
                        job_id,
                        mlflow_run_id,
                        title,
                        content,
                        content_sha256,
                        metadata,
                        updated_at
                    )
                    VALUES (
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s::jsonb,
                        NOW()
                    )
                    ON CONFLICT (job_id)
                    DO UPDATE SET
                        mlflow_run_id = EXCLUDED.mlflow_run_id,
                        title = EXCLUDED.title,
                        content = EXCLUDED.content,
                        content_sha256 = EXCLUDED.content_sha256,
                        metadata = EXCLUDED.metadata,
                        updated_at = NOW()
                    RETURNING id
                    """,
                    (
                        document.job_id,
                        document.mlflow_run_id,
                        document.title,
                        document.content,
                        document.content_sha256,
                        json.dumps(
                            document.metadata
                        ),
                    ),
                )

                row = cursor.fetchone()

                if row is None:
                    raise RuntimeError(
                        "Document insert did not "
                        "return an ID"
                    )

                document_id = int(
                    row[0]
                )

                cursor.execute(
                    """
                    DELETE FROM rag_chunks
                    WHERE document_id = %s
                    """,
                    (document_id,),
                )

                for chunk, embedding in zip(
                    document.chunks,
                    embeddings,
                    strict=True,
                ):
                    cursor.execute(
                        """
                        INSERT INTO rag_chunks (
                            document_id,
                            chunk_index,
                            content,
                            embedding,
                            metadata
                        )
                        VALUES (
                            %s,
                            %s,
                            %s,
                            %s::vector,
                            %s::jsonb
                        )
                        """,
                        (
                            document_id,
                            chunk.index,
                            chunk.content,
                            vector_literal(
                                embedding
                            ),
                            json.dumps(
                                chunk.metadata
                            ),
                        ),
                    )

            connection.commit()

        return document_id

    def semantic_search(
        self,
        query_embedding: list[float],
        *,
        limit: int = 3,
    ) -> list[SearchResult]:
        """Return nearest chunks using cosine similarity."""

        if limit < 1:
            raise ValueError(
                "limit must be at least 1"
            )

        query_vector = vector_literal(
            query_embedding
        )

        with self._connect() as connection, connection.cursor() as cursor:
            cursor.execute(
                """
                    SELECT
                        c.id,
                        c.document_id,
                        d.job_id,
                        c.chunk_index,
                        c.content,
                        c.metadata,
                        1 - (
                            c.embedding <=> %s::vector
                        ) AS similarity
                    FROM rag_chunks AS c
                    JOIN rag_documents AS d
                        ON d.id = c.document_id
                    WHERE c.embedding IS NOT NULL
                    ORDER BY
                        c.embedding <=> %s::vector
                    LIMIT %s
                    """,
                (
                    query_vector,
                    query_vector,
                    limit,
                ),
            )

            rows = cursor.fetchall()

        return [
            SearchResult(
                chunk_id=int(row[0]),
                document_id=int(row[1]),
                job_id=str(row[2]),
                chunk_index=int(row[3]),
                content=str(row[4]),
                metadata=(
                    row[5]
                    if isinstance(
                        row[5],
                        dict,
                    )
                    else json.loads(
                        row[5]
                    )
                ),
                similarity=float(row[6]),
            )
            for row in rows
        ]
