# Phase 08 — RAG Assistant (Deferred)

## Objective

Add a local read-only football analysis assistant using pgvector, embeddings, retrieval,
and Ollama only after the MLOps core is stable.

## Decision

Deferred for v0.1.0. Phases 5–7 are authored but await real Ubuntu evidence for
Compose, K3s, monitoring, and GitOps. Adding an LLM before those foundations are
running would increase scope without strengthening the platform core.

## Planned architecture

```text
analysis reports/docs -> chunking -> local embedding model -> PostgreSQL + pgvector
                                                    |
question -> retrieval -> grounded context -> Ollama -> read-only answer
```

## Preconditions

- Compose, K3s, Prometheus/Grafana, and Argo CD are validated on Ubuntu.
- PostgreSQL is migrated to an image that includes pgvector.
- A CPU-compatible Ollama model and embedding model are measured on the VM.
- Retrieved sources and answer limitations are visible in the API response.

## Why this is the correct scope decision

RAG is an optional product feature. Model lifecycle, serving, security, deployment,
and observability are the portfolio’s MLOps objective and must remain the priority.
