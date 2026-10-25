"""MLflow tracking utilities for football video analysis."""

import hashlib
import json
import os
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

import mlflow

from footballmatch_api.cv.pipeline import AnalysisSummary


def _package_version(package_name: str) -> str:
    """Return an installed package version without importing the package."""

    try:
        return version(package_name)
    except PackageNotFoundError:
        return "unknown"


def _sha256(path: Path) -> str:
    """Compute the SHA256 digest of a file without loading it fully into memory."""

    digest = hashlib.sha256()

    with path.open("rb") as file_object:
        while chunk := file_object.read(1024 * 1024):
            digest.update(chunk)

    return digest.hexdigest()


def track_analysis_run(
    summary: AnalysisSummary,
    *,
    confidence_threshold: float,
    requested_sample_fps: float,
    summary_path: Path,
    annotated_video_path: Path,
    tracking_uri: str | None = None,
    tracking_directory: Path | None = None,
    experiment_name: str = "football-video-analysis",
    job_id: str | None = None,
    original_filename: str | None = None,
    device: str = "cpu",
) -> str:
    """Record one reproducible football-video analysis run in MLflow."""

    if tracking_uri:
        mlflow.set_tracking_uri(tracking_uri)
    elif tracking_directory is not None:
        tracking_directory.mkdir(
            parents=True,
            exist_ok=True,
        )
        mlflow.set_tracking_uri(
            tracking_directory.resolve().as_uri()
        )

    mlflow.set_experiment(experiment_name)

    input_path = Path(summary.input_path)

    input_size_bytes = (
        input_path.stat().st_size
        if input_path.exists()
        else 0
    )

    input_sha256 = (
        _sha256(input_path)
        if input_path.exists()
        else "unknown"
    )

    total_detections = sum(
        summary.detections_by_label.values()
    )

    inference_fps = (
        summary.frames_processed / summary.inference_seconds
        if summary.inference_seconds > 0
        else 0.0
    )

    average_inference_ms_per_frame = (
        summary.inference_seconds
        * 1000
        / summary.frames_processed
        if summary.frames_processed > 0
        else 0.0
    )

    detections_per_frame = (
        total_detections / summary.frames_processed
        if summary.frames_processed > 0
        else 0.0
    )

    run_name = (
        f"analysis-{job_id[:8]}"
        if job_id
        else None
    )

    git_commit = os.getenv(
        "FOOTBALLMATCH_GIT_COMMIT",
        "unknown",
    )

    git_dirty = os.getenv(
        "FOOTBALLMATCH_GIT_DIRTY",
        "unknown",
    )

    app_version = os.getenv(
        "FOOTBALLMATCH_APP_VERSION",
        "unknown",
    )

    torch_version = _package_version("torch")
    ultralytics_version = _package_version("ultralytics")

    with mlflow.start_run(
        run_name=run_name,
    ) as run:
        mlflow.log_params(
            {
                "model_name": summary.model_name,
                "confidence_threshold": confidence_threshold,
                "requested_sample_fps": requested_sample_fps,
                "effective_sample_fps": summary.effective_fps,
                "input_filename": (
                    original_filename
                    or input_path.name
                ),
                "input_size_bytes": input_size_bytes,
                "input_sha256": input_sha256,
                "video_duration_seconds": summary.duration_seconds,
                "device": device,
            }
        )

        metrics = {
            "frames_processed": float(
                summary.frames_processed
            ),
            "inference_seconds": summary.inference_seconds,
            "total_seconds": summary.total_seconds,
            "inference_fps": inference_fps,
            "average_inference_ms_per_frame": (
                average_inference_ms_per_frame
            ),
            "total_detections": float(
                total_detections
            ),
            "detections_per_frame": detections_per_frame,
        }

        for label, count in (
            summary.detections_by_label.items()
        ):
            metric_name = (
                "detections_"
                + label.replace(" ", "_")
            )

            metrics[metric_name] = float(count)

        mlflow.log_metrics(metrics)

        tags = {
            "workload": "football-video-analysis",
            "execution_mode": "local-cpu",
            "model_framework": "ultralytics-yolo",
            "git_commit": git_commit,
            "git_dirty": git_dirty,
            "app_version": app_version,
            "torch_version": torch_version,
            "ultralytics_version": ultralytics_version,
            "device": device,
        }

        if job_id:
            tags["job_id"] = job_id

        mlflow.set_tags(tags)

        mlflow.log_artifact(
            str(summary_path),
            artifact_path="run-output",
        )

        if annotated_video_path.exists():
            mlflow.log_artifact(
                str(annotated_video_path),
                artifact_path="run-output",
            )

        metadata_path = (
            summary_path.parent
            / "model-and-run.json"
        )

        metadata = {
            "job_id": job_id,
            "mlflow_run_id": run.info.run_id,
            "model_name": summary.model_name,
            "device": device,
            "git_commit": git_commit,
            "git_dirty": git_dirty,
            "app_version": app_version,
            "torch_version": torch_version,
            "ultralytics_version": ultralytics_version,
            "input": {
                "filename": (
                    original_filename
                    or input_path.name
                ),
                "size_bytes": input_size_bytes,
                "sha256": input_sha256,
                "duration_seconds": summary.duration_seconds,
            },
            "parameters": {
                "confidence_threshold": confidence_threshold,
                "requested_sample_fps": requested_sample_fps,
                "effective_sample_fps": summary.effective_fps,
            },
            "metrics": metrics,
        }

        metadata_path.write_text(
            json.dumps(
                metadata,
                indent=2,
            ),
            encoding="utf-8",
        )

        mlflow.log_artifact(
            str(metadata_path),
            artifact_path="metadata",
        )

        return run.info.run_id
