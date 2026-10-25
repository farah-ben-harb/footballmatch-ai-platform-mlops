"""In-memory asynchronous job service for local video analysis."""

import json
from collections.abc import Callable
from dataclasses import asdict, dataclass
from pathlib import Path
from threading import Lock, Thread
from typing import BinaryIO, ClassVar
from uuid import uuid4

from footballmatch_api.cv.detector import YoloDetector
from footballmatch_api.cv.pipeline import AnalysisSummary, analyze_video
from footballmatch_api.mlflow_tracking import track_analysis_run
from footballmatch_api.observability import (
    DETECTIONS,
    FRAMES_PROCESSED,
    INFERENCE_DURATION,
    VIDEO_JOBS,
)
from footballmatch_api.schemas import JobResponse


@dataclass
class AnalysisJob:
    """Mutable internal state for one local analysis request."""

    id: str
    original_filename: str
    input_path: Path
    confidence_threshold: float = 0.25
    sample_fps: float = 5.0
    status: str = "queued"
    error: str | None = None
    result: dict[str, object] | None = None
    mlflow_run_id: str | None = None


class AnalysisJobService:
    """Persist uploads locally and process one video in a daemon thread."""

    allowed_extensions: ClassVar[set[str]] = {
        ".mp4",
        ".mov",
        ".avi",
        ".mkv",
        ".webm",
    }

    def __init__(
        self,
        runtime_directory: Path,
        max_upload_size_bytes: int,
        mlflow_tracking_uri: str | None = None,
        mlflow_experiment_name: str = "football-video-analysis",
        detector_factory: Callable[[], YoloDetector] = YoloDetector,
        pipeline: Callable[..., AnalysisSummary] = analyze_video,
    ) -> None:
        self.runtime_directory = runtime_directory
        self.max_upload_size_bytes = max_upload_size_bytes
        self.mlflow_tracking_uri = mlflow_tracking_uri
        self.mlflow_experiment_name = mlflow_experiment_name
        self._detector_factory = detector_factory
        self._pipeline = pipeline
        self._jobs: dict[str, AnalysisJob] = {}
        self._lock = Lock()
        self._model_lock = Lock()
        self._detector: YoloDetector | None = None

    def save_upload(
        self,
        filename: str,
        file_object: BinaryIO,
        *,
        confidence_threshold: float = 0.25,
        sample_fps: float = 5.0,
    ) -> AnalysisJob:
        """Validate and stream an uploaded video to the runtime directory."""

        safe_name = Path(filename).name
        extension = Path(safe_name).suffix.lower()

        if extension not in self.allowed_extensions:
            raise ValueError(
                "Only MP4, MOV, AVI, MKV, and WebM video files are accepted"
            )

        job_id = str(uuid4())
        input_directory = self.runtime_directory / "uploads" / job_id
        input_directory.mkdir(parents=True, exist_ok=True)

        input_path = input_directory / f"input{extension}"
        bytes_written = 0

        with input_path.open("wb") as destination:
            while chunk := file_object.read(1024 * 1024):
                bytes_written += len(chunk)

                if bytes_written > self.max_upload_size_bytes:
                    destination.close()
                    input_path.unlink(missing_ok=True)
                    raise ValueError(
                        "Uploaded video exceeds the configured size limit"
                    )

                destination.write(chunk)

        job = AnalysisJob(
            id=job_id,
            original_filename=safe_name,
            input_path=input_path,
            confidence_threshold=confidence_threshold,
            sample_fps=sample_fps,
        )

        with self._lock:
            self._jobs[job_id] = job

        VIDEO_JOBS.labels(status="accepted").inc()

        return job

    def start(self, job_id: str) -> None:
        """Run the job asynchronously after its upload has been persisted."""

        Thread(
            target=self.run,
            args=(job_id,),
            daemon=True,
            name=f"analysis-{job_id}",
        ).start()

    def run(self, job_id: str) -> None:
        """Execute inference, persist outputs, and transition the job state."""

        job = self._get_internal(job_id)
        self._set_status(job_id, "running")

        output_directory = self.runtime_directory / "jobs" / job_id
        output_path = output_directory / "annotated.mp4"
        summary_path = output_directory / "summary.json"

        output_directory.mkdir(parents=True, exist_ok=True)

        try:
            detector = self._get_detector()

            summary = self._pipeline(
                job.input_path,
                output_path,
                detector,
                target_fps=job.sample_fps,
                confidence_threshold=job.confidence_threshold,
            )

            summary_path.write_text(
                json.dumps(asdict(summary), indent=2),
                encoding="utf-8",
            )

            run_id = track_analysis_run(
                summary,
                confidence_threshold=job.confidence_threshold,
                requested_sample_fps=job.sample_fps,
                summary_path=summary_path,
                annotated_video_path=output_path,
                tracking_uri=self.mlflow_tracking_uri,
                experiment_name=self.mlflow_experiment_name,
                job_id=job.id,
                original_filename=job.original_filename,
                device=detector.device,
            )

            with self._lock:
                completed_job = self._jobs[job_id]
                completed_job.status = "completed"
                completed_job.result = asdict(summary)
                completed_job.mlflow_run_id = run_id

            VIDEO_JOBS.labels(status="completed").inc()
            FRAMES_PROCESSED.inc(summary.frames_processed)
            INFERENCE_DURATION.observe(summary.inference_seconds)

            for label, count in summary.detections_by_label.items():
                DETECTIONS.labels(label=label).inc(count)

        except Exception as error:  # noqa: BLE001
            with self._lock:
                failed_job = self._jobs[job_id]
                failed_job.status = "failed"
                failed_job.error = str(error)

            VIDEO_JOBS.labels(status="failed").inc()

    def get(self, job_id: str) -> JobResponse | None:
        """Return a public snapshot of a job, if it exists."""

        with self._lock:
            job = self._jobs.get(job_id)

            if job is None:
                return None

            return JobResponse(
                id=job.id,
                status=job.status,  # type: ignore[arg-type]
                original_filename=job.original_filename,
                error=job.error,
                result=job.result,
                mlflow_run_id=job.mlflow_run_id,
            )

    def _get_detector(self) -> YoloDetector:
        """Load model weights once per process, not once per job or frame."""

        with self._model_lock:
            if self._detector is None:
                self._detector = self._detector_factory()

            return self._detector

    def _get_internal(self, job_id: str) -> AnalysisJob:
        with self._lock:
            return self._jobs[job_id]

    def _set_status(self, job_id: str, status: str) -> None:
        with self._lock:
            self._jobs[job_id].status = status
