# Phase 04 — Model Serving and Application Architecture

## Objective

Expose football video analysis through a safe, asynchronous FastAPI interface.

## Starting state

Phase 3 provided a local command-line inference pipeline and MLflow tracking, but
there was no client-facing API, upload validation, job lifecycle, or error contract.

## Architecture

```text
client
  | POST /analyze (multipart video)
  v
FastAPI validation + local upload persistence
  |
  v
queued job -> daemon thread -> load YOLO once -> pipeline -> MLflow
  |                                              |
  v                                              v
GET /jobs/{id}                           runtime/jobs/{id}/ outputs
GET /matches/{id}
```

## What was implemented

- `POST /analyze` accepts an MP4/MOV/AVI/MKV/WebM upload and returns `202 Accepted`.
- The service streams uploads to disk with a configurable 100 MB maximum.
- Jobs transition through `queued`, `running`, `completed`, or `failed`.
- `GET /jobs/{id}` exposes state, error, result summary, and MLflow run ID.
- `GET /matches/{id}` returns only completed results, otherwise `409 Conflict`.
- A lazy detector cache loads YOLO once per API process rather than per job.
- Runtime uploads and results remain local and ignored by Git.

## Files added or modified

- `src/footballmatch_api/config.py`
- `src/footballmatch_api/main.py`
- `src/footballmatch_api/schemas.py`
- `src/footballmatch_api/services/analysis_jobs.py`
- `tests/test_analysis_api.py`
- `tests/test_analysis_jobs.py`
- `README.md`

## Commands executed

```powershell
.\.venv\Scripts\python.exe -m uvicorn footballmatch_api.main:app --host 127.0.0.1 --port 8001
```

Starts the ASGI server locally. `--host 127.0.0.1` binds only to the local machine;
`--port 8001` avoids assuming port 8000 is available.

```powershell
Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8001/health
Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8001/ready
```

## Validation

- `/health` returned `200` with `{"status":"ok"}`.
- `/ready` returned `200` with the local environment.
- `GET /jobs/unknown` returned `404`.
- Full suite: 25 tests passed; Ruff passed.

## Security considerations

- Extension allow-list is an early validation layer, not proof of safe content.
- Uploads are streamed with a maximum size, rather than read into memory at once.
- The server binds to loopback in local validation.
- Future phases must add MIME/codec validation, virus scanning policy, authentication,
  rate limits, durable storage, and isolated worker processes.

## DevOps / MLOps best practices applied

- HTTP requests receive a fast acknowledgement, not a long-running inference response.
- State is explicit and terminal errors remain observable.
- Model loading is process-lifecycle work, not request/frame work.
- API schemas prevent raw Ultralytics objects leaking to clients.

## Limitations

- Jobs are in memory; an API restart loses status history.
- A daemon thread is not a durable queue or horizontally scalable worker model.
- Results are local paths and are not yet persisted in PostgreSQL.
- The API has no authentication or authorization.

## Next phase

Phase 5 introduces Docker Compose, PostgreSQL-backed services, CI, and DevSecOps
checks. The job runner will remain deliberately small until a real queue is justified.

## How I would explain this phase in an interview

> Video analysis is a long-running workload, so I use an asynchronous API contract:
> POST returns 202 and a job ID, while clients poll a resource representing lifecycle
> state. I cache the model once per service process and handle terminal errors without
> exposing model-framework details. For production, I would replace in-memory jobs and
> threads with durable storage and a worker queue.
