# Phase 05 — Docker Compose, CI, and DevSecOps

## Objective

Make the platform reproducible as local containers and enforce automated quality and
security checks in GitHub Actions.

## Architecture

```text
Compose network
  api (FastAPI, non-root) -> mlflow (HTTP) -> postgres (MLflow metadata)
                            -> named artifact volume
```

## What was implemented

- Hardened non-root API Dockerfile with FFmpeg/OpenCV runtime libraries.
- Compose services for API, PostgreSQL 16, and MLflow 2.22.5.
- Persistent named volumes for database, MLflow artifacts, and API runtime files.
- GitHub Actions jobs for Ruff, pytest, Gitleaks, Semgrep, Docker build, and Trivy.
- Configurable external MLflow URI in the API.

## Commands executed

```powershell
Copy-Item .env.example .env
docker compose up --build -d
docker compose ps
curl http://localhost:8000/health
```

`up --build -d` rebuilds images then runs services detached. `ps` shows health and
port mappings. Run these on Ubuntu because Docker is unavailable on the Windows host.

## Validation

- 25 tests passed and Ruff passed locally.
- Docker/Compose runtime validation is pending the Ubuntu VM.

## Security considerations

- `.env` is ignored; `.env.example` contains a non-secret placeholder only.
- The Compose database password must be changed in the local `.env`.
- Containers run as a non-root `app` user where possible.
- Gitleaks prevents accidental secrets; Semgrep performs static analysis; Trivy scans
  the API image for high/critical vulnerabilities.

## Limitations

- Compose is a single-host development topology, not an orchestrator.
- PostgreSQL currently backs MLflow; job state remains in memory.
- CI configuration is committed but will be validated when its PR is opened.

## How I would explain this phase in an interview

> Compose gives developers one reproducible command for a multi-service environment.
> CI ensures every change runs tests and static checks, while DevSecOps moves secret,
> code, and image scanning earlier in the delivery lifecycle.
