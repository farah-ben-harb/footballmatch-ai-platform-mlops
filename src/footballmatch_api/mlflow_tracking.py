"""Local MLflow experiment tracking for video-analysis runs."""

import json
from pathlib import Path

import mlflow

from footballmatch_api.cv.pipeline import AnalysisSummary

DEFAULT_EXPERIMENT_NAME = "football-video-analysis"


def track_analysis_run(
    summary: AnalysisSummary,
    *,
    confidence_threshold: float,
    requested_sample_fps: float,
    summary_path: Path,
    annotated_video_path: Path,
    tracking_directory: Path = Path("mlruns"),
    experiment_name: str = DEFAULT_EXPERIMENT_NAME,
    run_name: str | None = None,
) -> str:
    """Log one completed local analysis run and return its MLflow run identifier."""
    tracking_directory.mkdir(parents=True, exist_ok=True)
    mlflow.set_tracking_uri(tracking_directory.resolve().as_uri())
    mlflow.set_experiment(experiment_name)

    with mlflow.start_run(run_name=run_name) as run:
        mlflow.log_params(
            {
                "model_name": summary.model_name,
                "confidence_threshold": confidence_threshold,
                "requested_sample_fps": requested_sample_fps,
                "effective_sample_fps": summary.effective_fps,
                "input_path": summary.input_path,
            }
        )
        mlflow.log_metrics(
            {
                "frames_processed": summary.frames_processed,
                "inference_seconds": summary.inference_seconds,
                "total_seconds": summary.total_seconds,
                "inference_fps": summary.frames_processed / summary.inference_seconds,
                **{
                    f"detections_{label.replace(' ', '_')}": count
                    for label, count in summary.detections_by_label.items()
                },
            }
        )
        mlflow.set_tags(
            {
                "workload": "football-video-analysis",
                "execution_mode": "local-cpu",
                "model_framework": "ultralytics-yolo",
            }
        )
        mlflow.log_artifact(str(summary_path), artifact_path="run-output")
        mlflow.log_artifact(str(annotated_video_path), artifact_path="run-output")
        mlflow.log_dict(
            {
                "model_name": summary.model_name,
                "detection_labels": sorted(summary.detections_by_label),
                "summary": json.loads(summary_path.read_text(encoding="utf-8")),
            },
            "metadata/model-and-run.json",
        )
        return run.info.run_id
