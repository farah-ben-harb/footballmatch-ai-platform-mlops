from pathlib import Path
from time import perf_counter
from typing import Annotated

from fastapi import (
    FastAPI,
    File,
    Form,
    HTTPException,
    Request,
    Response,
    UploadFile,
    status,
)
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from footballmatch_api.config import settings
from footballmatch_api.observability import HTTP_DURATION, HTTP_REQUESTS
from footballmatch_api.schemas import JobAcceptedResponse, JobResponse
from footballmatch_api.services.analysis_jobs import AnalysisJobService

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
)

analysis_jobs = AnalysisJobService(
    runtime_directory=Path(settings.runtime_directory),
    max_upload_size_bytes=settings.max_upload_size_bytes,
    mlflow_tracking_uri=settings.mlflow_tracking_uri,
    mlflow_experiment_name=settings.mlflow_experiment_name,
)


@app.middleware("http")
async def observe_http_requests(request: Request, call_next):
    """Record request count and latency without including query data in labels."""

    started_at = perf_counter()

    response = await call_next(request)

    path = request.url.path

    HTTP_REQUESTS.labels(
        request.method,
        path,
        response.status_code,
    ).inc()

    HTTP_DURATION.labels(
        request.method,
        path,
    ).observe(
        perf_counter() - started_at
    )

    return response


@app.get("/health")
def health() -> dict[str, str]:
    """Return basic process health."""

    return {"status": "ok"}


@app.get("/ready")
def ready() -> dict[str, str]:
    """Return readiness for serving traffic."""

    return {
        "status": "ready",
        "environment": settings.environment,
    }


@app.get("/metrics", include_in_schema=False)
def metrics() -> Response:
    """Expose Prometheus metrics for scraping."""

    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )


@app.post(
    "/analyze",
    response_model=JobAcceptedResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def analyze_video_upload(
    file: Annotated[UploadFile, File()],
    confidence_threshold: Annotated[
        float,
        Form(gt=0.0, le=1.0),
    ] = 0.25,
    sample_fps: Annotated[
        float,
        Form(gt=0.0, le=60.0),
    ] = 5.0,
) -> JobAcceptedResponse:
    """Accept a video and schedule a background analysis job."""

    if file.filename is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Filename is required",
        )

    try:
        job = analysis_jobs.save_upload(
            file.filename,
            file.file,
            confidence_threshold=confidence_threshold,
            sample_fps=sample_fps,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(error),
        ) from error
    finally:
        file.file.close()

    analysis_jobs.start(job.id)

    return JobAcceptedResponse(
        id=job.id,
        status_url=f"/jobs/{job.id}",
    )


@app.get(
    "/jobs/{job_id}",
    response_model=JobResponse,
)
def get_job(job_id: str) -> JobResponse:
    """Return an analysis job state and, when complete, its summary."""

    job = analysis_jobs.get(job_id)

    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis job not found",
        )

    return job


@app.get(
    "/matches/{job_id}",
    response_model=JobResponse,
)
def get_match(job_id: str) -> JobResponse:
    """Expose a completed match-analysis result using the current job identifier."""

    job = get_job(job_id)

    if job.status != "completed":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Analysis is not complete",
        )

    return job
