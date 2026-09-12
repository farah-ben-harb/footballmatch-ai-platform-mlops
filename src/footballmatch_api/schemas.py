"""HTTP response schemas for the video-analysis API."""

from typing import Literal

from pydantic import BaseModel, Field

JobStatus = Literal["queued", "running", "completed", "failed"]


class JobResponse(BaseModel):
    """Current state and optional result of a video-analysis job."""

    id: str
    status: JobStatus
    original_filename: str
    error: str | None = None
    result: dict[str, object] | None = None
    mlflow_run_id: str | None = None


class JobAcceptedResponse(BaseModel):
    """Response returned immediately after a video was accepted."""

    id: str
    status: Literal["queued"] = "queued"
    status_url: str
    message: str = Field(default="Video accepted for asynchronous analysis.")
