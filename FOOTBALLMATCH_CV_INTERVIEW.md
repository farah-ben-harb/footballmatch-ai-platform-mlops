# FootballMatch AI Platform - CV and Interview Notes

## Positioning

FootballMatch is strongest as an MLOps and platform-engineering project: it
packages a CPU-first computer-vision workload behind an API, records lineage in
MLflow, exposes operational metrics, and provides Docker, Helm, Kubernetes, and
GitOps delivery assets. It should not be presented as a production football
analytics product or as a model-accuracy benchmark.

## Verified technologies

### MLOps CV

- Python, FastAPI, OpenCV, Ultralytics YOLO11, ByteTrack, scikit-learn K-Means
- MLflow Tracking and Model Registry aliases (`candidate`, `champion`)
- Model packaging with an MLflow PyFunc wrapper and smoke-test promotion gate
- Input SHA-256 lineage, parameters, metrics, tags, JSON summaries, and annotated
  video artifacts
- Optional sentence-transformers, PostgreSQL/pgvector, and Ollama RAG extension

### Cloud Engineering CV

- Docker and Docker Compose service topology
- Kubernetes/K3s deployment with Helm, PVC, probes, resources, and non-root pod
  security
- Argo CD desired-state configuration with immutable image digest and self-healing
- Azure Container Apps demo path documented with scale-to-zero and commit-SHA image
- Prometheus and Grafana observability with application metrics and dashboard

### Infrastructure / SRE CV

- CI gates with pytest, Ruff, Gitleaks, Semgrep, and Trivy
- Immutable GHCR image publication only after checks on `main`
- Health/readiness endpoints, request latency metrics, job metrics, and resource
  limits
- Separation of application, tracking, database, and observability services
- Explicit limitations and rollback prerequisites for stateful volumes and model
  artifacts

## Recommended CV bullets

### French

- Conçu une plateforme MLOps Python/FastAPI pour analyser des vidéos de football
  avec YOLO11, ByteTrack et OpenCV, puis produire des vidéos annotées et des
  résumés structurés.
- Mis en place le suivi d'expériences et le registre de modèles MLflow avec
  validation smoke-test, alias `candidate/champion`, paramètres, métriques,
  artefacts et empreinte SHA-256 des entrées.
- Industrialisé le packaging et la livraison avec Docker, GitHub Actions, Gitleaks,
  Semgrep, Trivy, Helm, Kubernetes/K3s, Prometheus, Grafana et Argo CD.

### English

- Built a Python/FastAPI MLOps platform for football-video analysis using YOLO11,
  ByteTrack, and OpenCV, producing annotated videos and structured summaries.
- Implemented MLflow experiment tracking and model registry promotion with a
  smoke-test gate, `candidate/champion` aliases, lineage metadata, metrics,
  artifacts, and SHA-256 input hashes.
- Industrialized packaging and delivery with Docker, GitHub Actions, Gitleaks,
  Semgrep, Trivy, Helm, Kubernetes/K3s, Prometheus, Grafana, and Argo CD.

Do not add claims of measured accuracy, production availability, high availability,
or current Azure reachability unless new evidence is captured.

## 30-second presentation

### French

> FootballMatch est une plateforme MLOps locale qui transforme une vidéo de match
> en vidéo annotée et en métriques traçables. J'ai relié une API FastAPI à YOLO11,
> ByteTrack et un clustering de couleurs, puis ajouté MLflow pour la traçabilité,
> des contrôles de promotion de modèle, des métriques Prometheus et une livraison
> Docker/Kubernetes/Helm/Argo CD validée par CI.

### English

> FootballMatch is a local-first MLOps platform that turns a match video into
> annotated output and traceable metrics. I connected FastAPI with YOLO11,
> ByteTrack, and colour clustering, added MLflow lineage and model-promotion
> gates, and packaged the workload with Docker, Kubernetes, Helm, Argo CD, and CI
> security controls.

## Two-minute presentation structure

1. Start with the problem: demonstrate how an AI workload moves from video input
   to a reproducible, observable service.
2. Explain the request path: upload, bounded local persistence, asynchronous job,
   sampled frames, YOLO/ByteTrack inference, annotated video, JSON summary.
3. Explain lineage: MLflow stores parameters, hashes, metrics, tags, model version,
   and artifacts; a candidate is smoke-tested before champion promotion.
4. Explain platform work: non-root container, Helm probes and resources, immutable
   image reference, Prometheus/Grafana, and Argo CD desired state.
5. Finish with honesty: job state is in memory, the API is not authenticated, and
   model quality still needs a labelled benchmark before production decisions.

## Likely technical questions

### Why sample frames instead of processing every frame?

Sampling reduces CPU cost and makes runtime predictable. The effective FPS is
recorded, but the trade-off can miss short events; a quality benchmark is needed
before changing the target FPS.

### Why ByteTrack and why reset it?

ByteTrack supplies object identities across sequential frames. The detector state
is reset before each video so IDs from one job do not leak into another job.

### Do cluster IDs identify teams?

No. K-Means groups jersey-colour features into deterministic labels. The labels are
not semantic team identities and are not validated against ground truth.

### What does MLflow solve?

It records experiment inputs, parameters, metrics, artifacts, package versions, and
model lineage. The registry alias flow separates a tested candidate from the
champion selected by the API.

### Why is the API not horizontally scalable?

Jobs and detector state are process-local, and outputs use a local filesystem or
single PVC. A durable queue, shared object storage, persistent job store, and
worker coordination are required before multiple replicas.

### What do health and readiness prove?

`/health` proves the process responds. `/ready` reports application readiness and
environment, but it does not prove MLflow, PostgreSQL, Ollama, or model weights are
available. Dependency-aware readiness is a future reliability improvement.

### How is delivery controlled?

Pull requests run tests and scans without publishing. A push to `main` publishes an
image tagged with the commit SHA only after required jobs pass. Argo CD consumes the
Helm chart and an immutable image digest; runtime reconciliation still needs an
environment-specific validation.

### What is the main security boundary?

The current API is intended for a trusted local network. It has upload size and
extension checks, non-root containers, secret scanning, and no committed
credentials, but it still needs authentication, TLS, rate limiting, content
validation, and malware scanning before public exposure.

## Evidence and limits to state precisely

- Repository tests cover the core API, job service, video pipeline, detector,
  clustering, MLflow, registry gates, RAG, and health contracts.
- CI configuration includes tests, Ruff, Gitleaks, Semgrep, Docker build, and Trivy.
- The repository contains historical records for a local K3s run, an MLflow registry
  smoke test, and an Azure Container Apps demo. These records must be dated as
  historical evidence, not presented as current production monitoring.
- There is no committed ground-truth dataset, so precision, recall, identity
  switches, and team-classification accuracy are not established.
- There is no durable queue, object-storage lifecycle, multi-replica coordination,
  authentication layer, or tested disaster-recovery procedure.

