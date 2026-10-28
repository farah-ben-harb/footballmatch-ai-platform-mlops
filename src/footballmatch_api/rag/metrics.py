"""Prometheus metrics for the RAG pipeline."""

from prometheus_client import Counter, Histogram

RAG_REQUESTS_TOTAL = Counter(
    "footballmatch_rag_requests",
    "Total number of RAG requests.",
)

RAG_ERRORS_TOTAL = Counter(
    "footballmatch_rag_errors",
    "Total number of failed RAG requests.",
)

RAG_RETRIEVAL_SECONDS = Histogram(
    "footballmatch_rag_retrieval_seconds",
    "Time spent embedding the query and retrieving RAG context.",
)

RAG_GENERATION_SECONDS = Histogram(
    "footballmatch_rag_generation_seconds",
    "Time spent generating the answer with the LLM.",
)

RAG_TOTAL_SECONDS = Histogram(
    "footballmatch_rag_total_seconds",
    "Total duration of a RAG request.",
)
