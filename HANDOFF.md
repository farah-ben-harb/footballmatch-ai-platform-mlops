# Handoff - FootballMatch AI Platform

## Project

`FootballMatch AI Platform`

Goal: build a fully local, free, production-oriented MLOps / AI Platform for football match video analysis.

Primary focus:

- MLOps / AI Platform / DevOps: 70-80%
- Computer vision workload: 20-30%
- RAG / GenAI: optional after the core platform is stable

## Canonical Repository

Local repo root:

```text
D:\Projects\football-match-ai-platform
```

GitHub remote:

```text
https://github.com/farah-ben-harb/footballmatch-ai-platform-mlops.git
```

Current branch:

```text
feat/project-foundation
```

Current Git state at handoff:

```text
No commits yet on feat/project-foundation
Untracked project files exist locally
```

## Important Working Rules

- The user is implementing and learning.
- Codex may inspect, explain, guide, and review.
- Codex should not make repository changes unless explicitly authorized.
- No installs, deployments, destructive commands, or configuration-changing commands unless explicitly authorized.
- Keep Git history clean.
- Do not work directly on `main` for features.
- Use Conventional Commit messages.

## Phase 0 Status

Status:

```text
Paused
```

Reason:

The Ubuntu VM SSH connection will be used later. The full environment audit has not been completed yet.

Pending Phase 0 VM audit commands:

```bash
whoami
hostname
pwd
uname -a
cat /etc/os-release
lscpu
free -h
df -hT
lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINTS
```

Phase 0 Definition of Done is not yet satisfied.

## Phase 1 Status

Status:

```text
In progress, mostly implemented locally
```

Implemented files:

```text
README.md
.gitignore
.env.example
.dockerignore
Dockerfile
pyproject.toml
src/footballmatch_api/__init__.py
src/footballmatch_api/config.py
src/footballmatch_api/main.py
tests/test_health.py
docs/phases/phase-01-project-foundation.md
docs/learning/phase-01-project-foundation-concepts.md
HANDOFF.md
```

API endpoints:

```text
GET /health
GET /ready
```

Observed endpoint results:

```text
GET /health -> {"status": "ok"}
GET /ready  -> {"status": "ready", "environment": "local"}
```

Validation already completed:

```text
ruff: All checks passed
pytest: 2 passed
```

Known warning:

```text
FastAPI / Starlette emitted deprecation warnings related to TestClient/httpx.
The tests still passed.
```

Known limitation:

```text
Docker build has not been validated because the docker command was unavailable in the current Windows shell.
```

## Important Cleanup Before Commit

After running editable install, generated files appeared locally:

```text
src/footballmatch_ai_platform.egg-info/
.pytest_cache/
.ruff_cache/
__pycache__/
```

Before committing, ensure generated files are ignored and not staged.

Recommended `.gitignore` addition if not already present:

```gitignore
*.egg-info/
```

Then verify:

```powershell
cd D:\Projects\football-match-ai-platform
git status --short --branch
```

Generated cache folders should not be committed.

## Recommended Next Commands

Review changes:

```powershell
cd D:\Projects\football-match-ai-platform
git add -N .
git diff --stat
git diff
```

Run validation:

```powershell
.venv\Scripts\python -m ruff check .
.venv\Scripts\python -m pytest
```

Commit and push after review:

```powershell
git add .
git status --short --branch
git commit -m "feat(api): add project foundation"
git push -u origin feat/project-foundation
```

## Suggested Pull Request

Title:

```text
feat(api): add project foundation
```

Summary:

```text
Adds the initial FastAPI project foundation with health and readiness endpoints, project configuration, tests, linting, Docker packaging, and Phase 1 documentation.
```

Changes:

- Add FastAPI app package.
- Add `/health` and `/ready` endpoints.
- Add Pydantic settings.
- Add pytest coverage.
- Add Ruff configuration.
- Add Dockerfile and `.dockerignore`.
- Add `.gitignore` and `.env.example`.
- Add Phase 1 documentation.

Testing:

```text
.venv\Scripts\python -m ruff check .
.venv\Scripts\python -m pytest
```

Security considerations:

- `.env` is ignored.
- `.env.example` documents variables without storing secrets.
- Dockerfile uses a non-root application user.
- Runtime outputs and local artifacts are ignored.

Known limitations:

- Docker build not validated yet.
- VM audit still pending.
- No computer vision pipeline yet.

Next steps:

- Finish Phase 1 commit and PR.
- Validate Docker on Ubuntu VM or another environment with Docker available.
- Start Phase 2: Computer Vision baseline.

## Seven-Day Execution Priority

Day 1:

- Finish Phase 0 evidence later if possible.
- Finish Phase 1 foundation.

Day 2:

- Phase 2 CV baseline.

Day 3:

- Phase 3 ML fundamentals + MLflow.
- Phase 4 model serving shape.

Day 4:

- Phase 5 Docker Compose + CI + DevSecOps.

Day 5:

- Phase 6 K3s + Helm + Observability.

Day 6:

- Phase 7 GitOps + Argo CD.

Day 7:

- Hardening and portfolio release.
- Phase 8 RAG only if the core is stable.

## Interview Story So Far

The project starts with a minimal production-style API foundation. It uses FastAPI for the service layer, Pydantic Settings for environment-based configuration, pytest for automated tests, Ruff for code quality, and Docker packaging for later deployment. Health and readiness endpoints prepare the app for Kubernetes-style operations.

Short answer to remember:

```text
I first built a clean FastAPI foundation with health and readiness endpoints, tests, linting, and Docker packaging. This creates a reliable service boundary before adding computer vision, MLflow, CI/CD, Kubernetes, observability, and GitOps.
```
