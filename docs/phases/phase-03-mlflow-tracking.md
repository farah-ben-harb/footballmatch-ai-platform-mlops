# Phase 03 — ML Fundamentals and MLflow Tracking

## Objective

Make video-analysis runs comparable and traceable by recording parameters, metrics,
tags, and artifacts in a fully local MLflow backend. Add a small self-built ML
component using K-Means jersey-colour features.

## Starting state

Phase 2 could process a video with YOLO and write an annotated MP4 and JSON summary,
but runs were only visible in terminal output and local artifact files.

## Architecture

```text
video -> sampled YOLO inference -> summary + annotated MP4
                                  |
                                  v
                         local MLflow file store (mlruns/)
                    params + metrics + tags + artifacts
```

## What was implemented

- MLflow 2.22.5 configured with a local file-based tracking URI.
- One run logs model name, confidence threshold, requested/effective sample FPS,
  frame count, inference duration, total duration, and detection counts.
- The JSON summary, annotated video, and run/model metadata are logged as artifacts.
- `TeamColorClusterer` wraps scikit-learn K-Means for two-team colour clustering.
- Unit tests use a fake MLflow client, keeping tests offline and deterministic.

## Files added or modified

- `pyproject.toml`
- `scripts/analyze_video.py`
- `src/footballmatch_api/ml/team_clustering.py`
- `src/footballmatch_api/mlflow_tracking.py`
- `tests/test_team_clustering.py`
- `tests/test_mlflow_tracking.py`
- `README.md`

## Commands executed

```powershell
.\.venv\Scripts\python.exe scripts\analyze_video.py --input data\raw\match.mp4 --output artifacts\annotated-match-mlflow.mp4 --summary artifacts\analysis-summary-mlflow.json --sample-fps 5 --confidence 0.25 --run-name phase-03-cv-baseline
```

This creates a completed local MLflow run and stores its files under ignored `mlruns/`.

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m ruff check .
```

## Validation

- 25 tests passed.
- Ruff passed.
- MLflow run ID: `93db66858fdd479f8f19c0d22d69a7c4`.
- The local store includes params, metrics, tags, JSON metadata, and both output artifacts.

## Evidence

```text
Experiment: football-video-analysis
Model: yolo11n.pt
Frames processed: 190
Person detections: 745
Sports-ball detections: 67
Inference time: 119.07 s
Total time: 168.12 s
```

The second inference run was slower than Phase 2 because the local Windows CPU was
under heavier load. This is recorded as environment-sensitive evidence, not a stable
performance claim.

## Errors encountered

MLflow 3.16 imported extremely slowly/hung in this Windows environment. MLflow was
pinned to 2.22.5, which imported and tracked successfully. MLflow 2 emits two
third-party Pydantic deprecation warnings during tests; project tests still pass.

## Security considerations

- `mlruns/` remains ignored by Git because it can contain source paths and large artifacts.
- No cloud tracking URI, token, or external account is used.
- Model names and execution mode are tags, enabling later audit and comparison.

## DevOps / MLOps best practices applied

- Log configuration with outputs, rather than output metrics alone.
- Keep model-framework objects behind application contracts.
- Store artifacts alongside a run so a metric is explainable.
- Use deterministic K-Means random state for reproducible learning examples.

## Git / PR summary

Branch: `feat/mlflow-tracking`.

Suggested PR title: `feat(mlflow): track local video analysis experiments`

## Limitations

- File-based MLflow is appropriate only for local single-user work.
- K-Means clusters colours, not semantic team identities; cluster 0/1 labels can swap.
- Model registration is deferred until a persistent database-backed MLflow deployment.

## Next phase

Expose video analysis through an asynchronous FastAPI job interface.

## How I would explain this phase in an interview

> MLflow is not the ML model. It is the system of record for model runs. I log the
> detector configuration, performance and detection metrics, metadata, and actual
> output artifacts together, so I can compare runs and investigate a result later.
