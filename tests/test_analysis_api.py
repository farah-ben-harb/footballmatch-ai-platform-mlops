from io import BytesIO
from pathlib import Path

import httpx
import pytest

from footballmatch_api import main
from footballmatch_api.schemas import JobResponse
from footballmatch_api.services.analysis_jobs import AnalysisJob

pytestmark = pytest.mark.anyio


class FakeJobs:
    def __init__(self) -> None:
        self.job = AnalysisJob(
            "job-1",
            "match.mp4",
            Path("runtime/input.mp4"),
        )
        self.started: list[str] = []

    def save_upload(
        self,
        filename: str,
        file_object: BytesIO,
        *,
        confidence_threshold: float = 0.25,
        sample_fps: float = 5.0,
    ) -> AnalysisJob:
        del filename, file_object
        self.job.confidence_threshold = confidence_threshold
        self.job.sample_fps = sample_fps
        return self.job

    def start(self, job_id: str) -> None:
        self.started.append(job_id)

    def get(self, job_id: str):
        if job_id != self.job.id:
            return None

        return JobResponse(
            id=job_id,
            status="queued",
            original_filename="match.mp4",
        )


async def test_analyze_returns_accepted_job(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_jobs = FakeJobs()
    monkeypatch.setattr(main, "analysis_jobs", fake_jobs)

    transport = httpx.ASGITransport(app=main.app)

    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        response = await client.post(
            "/analyze",
            files={
                "file": (
                    "match.mp4",
                    b"video",
                    "video/mp4",
                )
            },
        )

    assert response.status_code == 202
    assert response.json()["id"] == "job-1"
    assert fake_jobs.started == ["job-1"]


async def test_analyze_accepts_inference_parameters(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_jobs = FakeJobs()
    monkeypatch.setattr(main, "analysis_jobs", fake_jobs)

    transport = httpx.ASGITransport(app=main.app)

    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        response = await client.post(
            "/analyze",
            files={
                "file": (
                    "match.mp4",
                    b"video",
                    "video/mp4",
                )
            },
            data={
                "confidence_threshold": "0.4",
                "sample_fps": "3",
            },
        )

    assert response.status_code == 202
    assert fake_jobs.job.confidence_threshold == 0.4
    assert fake_jobs.job.sample_fps == 3.0


async def test_analyze_rejects_invalid_confidence_threshold(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_jobs = FakeJobs()
    monkeypatch.setattr(main, "analysis_jobs", fake_jobs)

    transport = httpx.ASGITransport(app=main.app)

    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        response = await client.post(
            "/analyze",
            files={
                "file": (
                    "match.mp4",
                    b"video",
                    "video/mp4",
                )
            },
            data={
                "confidence_threshold": "2",
                "sample_fps": "3",
            },
        )

    assert response.status_code == 422


async def test_get_job_returns_404_for_unknown_job(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_jobs = FakeJobs()
    monkeypatch.setattr(main, "analysis_jobs", fake_jobs)

    transport = httpx.ASGITransport(app=main.app)

    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        response = await client.get("/jobs/unknown")

    assert response.status_code == 404
