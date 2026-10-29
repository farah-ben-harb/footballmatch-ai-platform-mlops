# Concepts  Phase 08: RAG assistant

## Mental model / workflow

```text
analysis result -> text chunks -> embedding vectors -> pgvector
question -> embedding -> nearest chunks -> Ollama -> sourced answer
```

## LLM and GenAI

### Definition

Generative AI creates new content. A large language model (LLM) is a
probabilistic model that predicts token sequences and can generate text.

### Why it exists and how it works

An LLM learns language patterns from training data and uses the current
prompt context to predict subsequent tokens. It does not automatically
know current match results or private project data.

### Architecture position and example

Ollama serves a local small LLM after retrieval supplies football-analysis
context. The project does not call a paid hosted API.

### Alternatives, advantages, and limitations

Hosted LLMs may be faster or stronger but require an external provider.
A local model protects the no-paid-cloud goal but is slower on CPU and
may still hallucinate.

### Production and security considerations

Limit prompt size, timeouts, and untrusted input. Never send credentials or
private content to an external model without authorization.

## Embeddings and pgvector

### Definition

An embedding maps text to a fixed-length numeric vector. pgvector adds
vector columns and similarity indexes to PostgreSQL.

### Why they exist and how they work

Semantically related text tends to have nearby embeddings. The project
normalizes 384-dimensional vectors from all-MiniLM-L6-v2 and searches with
cosine distance. An HNSW index accelerates approximate nearest-neighbor
search as the corpus grows.

### Architecture position and example

Analysis chunks and their embeddings live in `rag_chunks`; `rag_documents`
keeps the job ID, MLflow run ID, hash, and metadata. A question is embedded
with the same model before searching.

### Alternatives, advantages, and limitations

Full-text search matches words and can complement vectors. A dedicated
vector database adds features but another service; pgvector reuses the
existing PostgreSQL instance. HNSW trades memory and build cost for faster
approximate search. For tiny datasets, an exact scan may suffice.

### Security and common mistakes

Never put passwords in connection strings committed to Git. Keep embedding
dimensions consistent with the database schema; using a different model
without migration breaks inserts or makes comparisons meaningless.

## Retrieval Augmented Generation

### Definition

RAG retrieves relevant documents at query time and includes them in the
LLM prompt. The model weights are unchanged.

### Why it exists and how it works

Training an LLM on every new match is impractical. Retrieval supplies current
analysis evidence. The service embeds a question, queries pgvector, builds
a bounded context, asks Ollama, and returns the answer with source chunks.

### Architecture position and example

`POST /rag/ask` invokes the embedder, repository, and generator in that
order. `GET /rag/status` reports configuration without loading the model.

### Alternatives, advantages, and limitations

Fine-tuning changes weights; RAG changes context. A simple chatbot may
generate without retrieval. RAG improves traceability but cannot guarantee
truth; retrieved context can be wrong, incomplete, or malicious.

### Production and security considerations

Evaluate retrieval and answer quality separately. Bound request sizes and
timeouts, log failures without secrets, and treat retrieved text as
untrusted input. The assistant is read-only; it does not execute actions.

## Optional indexing and failure isolation

### Definition and why it exists

Automatic indexing is a feature flag-controlled best-effort step after a
successful analysis job. It creates a document and embeddings for that job.

### How it works in the project

`FOOTBALLMATCH_RAG_AUTO_INDEX` defaults to false. When enabled, indexing
runs after the video and MLflow work completes. Errors are logged without
changing the completed video-job status.

### Alternatives and production considerations

A durable queue would be safer for retries and scaling. The current
in-process job model is appropriate for a single-node learning MVP but
cannot guarantee retry after a process restart.

## KFP definition

### Definition and architecture position

Kubeflow Pipelines (KFP) describes a directed workflow of components.
The repository contains a KFP v2 pipeline definition and compiled YAML
for submit, wait, and validation steps.

### Limitation

Compiling a pipeline does not mean a Kubeflow cluster is installed or that
the pipeline was executed. This project keeps the full Kubeflow control
plane outside the small VM scope.

## Commands to remember

| Command | Role | When to use |
| --- | --- | --- |
| `docker compose config` | Validate service configuration | Before starting Compose |
| `psql -c 'SELECT extname FROM pg_extension'` | Check pgvector extension | After database setup |
| `python scripts/index_rag_document.py FILE.json` | Index an analysis | During data preparation |
| `python scripts/ask_rag.py "QUESTION"` | Test retrieval and generation | During local validation |
| `curl -X POST /rag/ask` | Test the served RAG API | After deployment |

## Interview questions and answers

1. **Embedding versus LLM?** An embedding represents semantic similarity;
   an LLM generates text.
2. **RAG versus fine-tuning?** RAG adds retrieved context at inference time;
   fine-tuning updates model weights.
3. **PostgreSQL versus pgvector?** PostgreSQL is the database; pgvector is
   its vector data type and similarity-search extension.
4. **Why use HNSW?** It speeds approximate nearest-neighbor search for larger
   vector collections.
5. **Why return sources?** They let users inspect what evidence supported
   the answer.
6. **Does RAG eliminate hallucinations?** No. Retrieval and generation can
   both fail, so quality must be evaluated.
7. **Why not an autonomous agent?** The use case only needs read-only
   retrieval and answer generation; action execution adds unnecessary risk.
8. **Why isolate indexing failures?** A database outage should not turn a
   successful video analysis into a failed job.
9. **Is a compiled KFP YAML proof of execution?** No. It is only a workflow
   specification until run on a compatible control plane.

## External services from a K3s Pod

### Definition and why it exists

A Pod has its own network namespace. A Compose service name resolves only on
its Docker network, so a Pod needs a reachable address for PostgreSQL, MLflow,
and Ollama. On this single-node VM, the Docker host bridge provides that path.

### How it works and architecture position

The database container exposes port 5432 through a host-bound port 15432.
The binding defaults to loopback for safety; the VM's ignored `.env` chooses
a host bridge address reachable from K3s. Helm stores non-secret endpoints in
a ConfigMap and injects the database password from a Kubernetes Secret.
The Pod connects to PostgreSQL, retrieves pgvector chunks, then calls Ollama.

### Alternatives and production considerations

Alternatives include a Kubernetes Service plus EndpointSlice for an external
database, a stable DNS name, or moving PostgreSQL into Kubernetes. The bridge
is the smallest demonstrable choice for this single-node VM. It is tied to
the local host network and must be replaced for multi-node scheduling.
A Kubernetes Secret is configuration separation, not encryption by itself;
limit RBAC access and enable encryption at rest in a production cluster.
A connection timeout prevents a dead network path from hanging the API;
the API maps database connection errors to HTTP 503 without leaking details.

### Interview questions and answers

1. **Why did Compose DNS fail in K3s?** The Pod and Compose service are in
   different network namespaces and DNS domains.
2. **Why use a Secret?** It keeps the database password out of Helm values,
   ConfigMaps, Git, and response bodies.
3. **Why return 503 on a database outage?** The service is temporarily
   unable to answer; callers can distinguish dependency failure.
4. **Why add a connection timeout?** It bounds waiting on an unreachable host.
5. **Why is a host bridge only a local solution?** It assumes one node and
   host-specific networking; multi-node clusters need a stable endpoint.
