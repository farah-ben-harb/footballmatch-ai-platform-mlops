# FootballMatch AI Platform

Production-oriented, local-first MLOps learning project that turns football match
video analysis into an observable, versioned, testable AI workload.

## Delivery status

The application, tests, CI security controls, container build, Helm chart, and GitOps
manifests are implemented. The GitHub Actions workflow has successfully built and
published the container image to GHCR. Runtime validation of Docker Compose, local K3s,
Prometheus/Grafana, and Argo CD is the remaining delivery milestone; it is deliberately
not presented as completed work.

## Problem and scope

The project intentionally prioritizes MLOps and platform engineering over CV research.
A CPU-friendly pretrained YOLO detector is the workload; FastAPI, MLflow, Docker,
Kubernetes, observability, and GitOps are the platform around it.

```mermaid
flowchart LR
  V[Football video] --> A[FastAPI /analyze]
  A --> J[Asynchronous analysis job]
  J --> CV[OpenCV + sampled YOLO]
  CV --> O[Annotated MP4 + JSON]
  CV --> M[MLflow experiments]
  M --> P[PostgreSQL backend in Compose]
  A --> X[/metrics]
  X --> PR[Prometheus]
  PR --> G[Grafana]
  GH[GitHub Actions] --> I[GHCR image]
  GI[Argo CD] --> K[K3s + Helm]
```

## Implemented capabilities

- FastAPI `/health`, `/ready`, `/metrics`, `/analyze`, `/jobs/{id}`, and `/matches/{id}`.
- CPU-first YOLO11n video inference with deterministic frame sampling.
- Annotated MP4 and JSON summaries; observed baseline processed 190 frames with person
  and sports-ball detections.
- Local MLflow runs with parameters, metrics, tags, output artifacts, and model metadata.
- Explainable K-Means jersey-colour clustering component.
- Asynchronous job lifecycle with explicit `queued`, `running`, `completed`, and `failed` states.
- Docker/Compose definitions for API, MLflow, and PostgreSQL.
- GitHub Actions quality, secret, SAST, container, and image-publication workflow.
- Helm chart, Prometheus metrics, Grafana dashboard definition, and Argo CD Application manifest.

## Run locally

Requirements: Python 3.10, FFmpeg, and a permitted football video at `data/raw/match.mp4`.

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe scripts\analyze_video.py --input data\raw\match.mp4
.\.venv\Scripts\python.exe -m uvicorn footballmatch_api.main:app --host 127.0.0.1 --port 8000
```

Upload with PowerShell:

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/analyze -Form @{ file = Get-Item data\raw\match.mp4 }
```

Poll the returned ID with `GET /jobs/{id}`. Generated data, artifacts, MLflow files,
model weights, and `.env` remain outside Git.

## Compose and deployment

Copy `.env.example` to `.env`, set a real local-only PostgreSQL password, then execute
on a local Docker host. On Windows, the intended host is Docker Desktop using its WSL2
backend; a local K3s cluster will be created with k3d.

```bash
docker compose up --build -d
docker compose ps
```

K3s, Prometheus/Grafana, and Argo CD commands are documented in `docs/phases/`.
The Helm chart is at `helm/footballmatch-ai-platform`; GitOps configuration is at
`gitops/argocd/footballmatch-application.yaml`.

## Testing and security

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m ruff check .
helm lint helm\footballmatch-ai-platform
```

GitHub Actions adds Gitleaks, Semgrep, a Docker build, and a blocking Trivy filesystem
scan for dependency and IaC vulnerabilities. A full scan of the pushed image is a
release-environment check to run on the local deployment host, where disk capacity is controlled.
Read [SECURITY.md](SECURITY.md) before using real data or deploying outside a local VM.

## Current limitations

- `person` does not separate player, referee, or spectator; counts are per frame, not unique identities.
- Jobs are in memory, so restarts lose their state and replicas are limited to one.
- Docker Compose, K3s, Prometheus/Grafana, and Argo CD manifests are authored and linted,
  but runtime deployment evidence is still pending on the local Docker Desktop/k3d host.
- RAG/Ollama is intentionally deferred until the MLOps core is proven stable.

## Documentation

- `docs/phases/`: implementation evidence, validation, limitations, and PR summaries.
- `docs/learning/`: concepts, trade-offs, and interview answers.
- `docs/release/`: v0.1.0 release checklist and portfolio evidence plan.
