# FootballMatch AI Platform

Production-oriented local MLOps and AI Platform learning project for football match video analysis.

## Current MVP

- FastAPI health and readiness endpoints.
- CPU-first YOLO football-video analysis.
- Annotated MP4 output and JSON inference metrics.
- Local MLflow experiment tracking for parameters, metrics, tags, and artifacts.
- Asynchronous FastAPI video-upload jobs with result polling.
- pytest and Ruff quality checks.

## Run the CV baseline

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe scripts\analyze_video.py --input data\raw\match.mp4
```

The command writes ignored local artifacts to `artifacts/annotated-match.mp4` and
`artifacts/analysis-summary.json`. The pretrained `yolo11n.pt` model detects
COCO `person` and `sports ball`; it does not distinguish players from referees.
MLflow run data is stored locally under `mlruns/`.

## Run the API

```powershell
.\.venv\Scripts\python.exe -m uvicorn footballmatch_api.main:app --host 127.0.0.1 --port 8000
```

`POST /analyze` accepts a permitted video and returns a job ID. Poll `GET /jobs/{id}`
until it reaches `completed` or `failed`; `GET /matches/{id}` returns completed results.

## Validation

```powershell
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m ruff check .
```
