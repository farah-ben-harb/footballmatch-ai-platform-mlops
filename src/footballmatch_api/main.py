from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, File, HTTPException, UploadFile, status

from footballmatch_api.config import settings
from footballmatch_api.schemas import JobAcceptedResponse, JobResponse
from footballmatch_api.services.analysis_jobs import AnalysisJobService

app = FastAPI(title=settings.app_name, version=settings.app_version)
analysis_jobs = AnalysisJobService(
    runtime_directory=Path(settings.runtime_directory),
    max_upload_size_bytes=settings.max_upload_size_bytes,
    mlflow_tracking_uri=settings.mlflow_tracking_uri,
    mlflow_experiment_name=settings.mlflow_experiment_name,
)


@app.get("/health")
def health() -> dict[str, str]:
    """Return basic process health."""

    return {"status": "ok"}


@app.get("/ready")
def ready() -> dict[str, str]:
    """Return readiness for serving traffic."""

    return {"status": "ready", "environment": settings.environment}


@app.post("/analyze", response_model=JobAcceptedResponse, status_code=status.HTTP_202_ACCEPTED)
def analyze_video_upload(file: Annotated[UploadFile, File()]) -> JobAcceptedResponse:
    """Accept a video and schedule a background analysis job."""
    if file.filename is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Filename is required")
    try:
        job = analysis_jobs.save_upload(file.filename, file.file)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(error)) from error
    finally:
        file.file.close()

    analysis_jobs.start(job.id)
    return JobAcceptedResponse(id=job.id, status_url=f"/jobs/{job.id}")


@app.get("/jobs/{job_id}", response_model=JobResponse)
def get_job(job_id: str) -> JobResponse:
    """Return an analysis job state and, when complete, its summary."""
    job = analysis_jobs.get(job_id)
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis job not found")
    return job


@app.get("/matches/{job_id}", response_model=JobResponse)
def get_match(job_id: str) -> JobResponse:
    """Expose a completed match-analysis result using the current job identifier."""
    job = get_job(job_id)
    if job.status != "completed":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Analysis is not complete")
    return job
