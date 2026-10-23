# Phase 01 - Project Foundation

## Objective

Create the first working application foundation for FootballMatch AI Platform.

## Starting state

The repository existed on branch `feat/project-foundation` and contained only Git metadata.

## Architecture

```text
Client
  |
  v
FastAPI application
  |
  +-- GET /health
  +-- GET /ready
```

## What was implemented

- Python package layout using `src/`
- FastAPI application
- `/health` endpoint
- `/ready` endpoint
- Pydantic settings object
- pytest tests using `httpx` ASGI transport
- Ruff lint configuration
- Dockerfile
- `.dockerignore`
- `.gitignore`

## Files added or modified

- `README.md`
- `.gitignore`
- `.dockerignore`
- `.env.example`
- `Dockerfile`
- `pyproject.toml`
- `src/footballmatch_api/__init__.py`
- `src/footballmatch_api/config.py`
- `src/footballmatch_api/main.py`
- `tests/test_health.py`
- `docs/phases/phase-01-project-foundation.md`
- `docs/learning/phase-01-project-foundation-concepts.md`

## Commands executed

### `python -m venv .venv`

Creates an isolated Python environment inside the project.

Important detail: dependencies installed into `.venv` do not affect the global Windows Python installation.

### `.venv\Scripts\python -m pip install --upgrade pip`

Upgrades `pip` inside the virtual environment.

### `.venv\Scripts\python -m pip install -e ".[dev]"`

Installs the project in editable mode with development dependencies.

Important flags:

- `-e`: editable install
- `".[dev]"`: install the package plus the optional `dev` dependency group

### `.venv\Scripts\python -m ruff check .`

Runs Python lint checks.

### `.venv\Scripts\python -m ruff check . --fix`

Automatically fixed import sorting.

### `.venv\Scripts\python -m pytest`

Runs the test suite.

### `.venv\Scripts\python -m uvicorn footballmatch_api.main:app --host 127.0.0.1 --port 8000`

Starts the FastAPI development server.

Important flags:

- `--host 127.0.0.1`: bind only to local machine
- `--port 8000`: listen on port 8000

## Validation

- API started successfully with Uvicorn.
- `/health` returned `{"status": "ok"}`.
- `/ready` returned `{"status": "ready", "environment": "local"}`.

## Tests executed

```text
2 passed
```

## Evidence

Ruff:

```text
All checks passed!
```

pytest:

```text
tests\test_health.py .. [100%]
2 passed
```

Warnings:

```text
No pytest warnings while using `httpx` ASGITransport for API tests.
```

## Errors encountered

Docker was not available in the current Windows shell.

```text
docker: The term 'docker' is not recognized
```

## Root causes

Docker CLI is not installed or not available on the Windows PATH.

## Fixes

Docker validation is deferred until Docker is available on the local deployment host.

## Security considerations

- `.env` files are ignored.
- `.env.example` documents expected environment variables without storing secrets.
- Runtime artifacts are ignored.
- Docker image runs as a non-root user.
- API binds to `127.0.0.1` during local development.

## DevOps / MLOps best practices applied

- `src/` Python package layout
- isolated virtual environment
- automated tests
- linting
- non-root container user
- health and readiness endpoints

## Git / PR summary

Suggested PR title:

`feat(api): add project foundation`

Summary:

- Add minimal FastAPI application.
- Add health and readiness endpoints.
- Add pytest coverage.
- Add Dockerfile and Docker ignore rules.
- Add project metadata and dependency configuration.

## Limitations

- Docker image build has not been validated because Docker is unavailable in the current shell.
- Local deployment-host capacity audit is still pending.
- No video processing exists yet.

## Next phase

Phase 2 will add a computer vision baseline for processing a short football video.

## How I would explain this phase in an interview

I created a minimal production-style API foundation with health and readiness endpoints, tests, linting, project metadata, and container packaging. This gives later ML and MLOps components a stable service boundary.
