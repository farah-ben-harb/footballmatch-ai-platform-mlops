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
- Compose services for API, PostgreSQL 16, and MLflow 3.17.2.
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
port mappings. Run these on the local Docker Desktop/WSL2 host.

## Validation

- Docker Compose ran API, PostgreSQL, and MLflow on the Ubuntu VM.
- PR #22 validated Python 3.12 tests, Semgrep, and Gitleaks after the upgrade.
- The image scan is a required release gate.

## Security considerations

- `.env` is ignored; `.env.example` contains a non-secret placeholder only.
- The Compose database password must be changed in the local `.env`.
- Containers run as a non-root `app` user where possible.
- Gitleaks detects likely committed secrets; Semgrep performs static analysis.
- Trivy blocks fixable HIGH/CRITICAL repository findings and fixable CRITICAL
  vulnerabilities in the built API image.
- Only the main-branch publish job can write packages.

## Limitations

- Compose is a single-host development topology, not an orchestrator.
- PostgreSQL currently backs MLflow; job state remains in memory.
- The CPU PyTorch image is large, so CI builds take several minutes.


## Security upgrade and migration

The first blocking image scan found eleven fixable CRITICAL findings in MLflow
2.22.5 and Pillow 12.3.0. Pillow 13 requires Python 3.11 or newer. API and
MLflow images now use Python 3.12; both MLflow client and server pin 3.17.2,
and the API pins Pillow 13.0.0.

For the PostgreSQL-backed MLflow server, take and verify a restricted backup;
build the new image; stop the server and other writers; run
`mlflow db upgrade <backend-store-url>`; restart MLflow; verify existing and
new runs. MLflow documents that migrations may not be transactional.
The verified backup is a rollback point, though restoring it overwrites
later writes.

CI publishes only after all checks pass on `main`. It uses a
`sha-<full-commit>` tag and records the OCI digest in the job summary.
The digest identifies image content even if a tag is reassigned.

## Errors, root causes, and fixes

- The image scan failed because old MLflow/Pillow packages had fixable CRITICAL
  CVEs. The fix coordinates package versions with the Python runtime.
- Creating a backup directly under `/data` failed because the directory is
  root-owned. The backup went into a user-owned directory with mode 0600.

## Git / PR summary

PR #22 contains image scanning, minimum workflow permissions, content-addressed
publication, and the dependency upgrade. Review `git status`, `git diff`,
and `git diff --staged` before each commit.

## How I would explain this phase in an interview

> Compose gives developers one reproducible command for a multi-service environment.
> CI ensures every change runs tests and static checks, while DevSecOps moves secret,
> code, and image scanning earlier in the delivery lifecycle.
