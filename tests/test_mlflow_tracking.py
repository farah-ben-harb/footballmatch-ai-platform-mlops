from contextlib import contextmanager
from pathlib import Path

from footballmatch_api import mlflow_tracking
from footballmatch_api.cv.pipeline import AnalysisSummary


class FakeRun:
    class Info:
        run_id = "run-123"

    info = Info()


class FakeMlflow:
    def __init__(self) -> None:
        self.params: dict[str, object] | None = None
        self.metrics: dict[str, float] | None = None
        self.tags: dict[str, str] | None = None
        self.artifacts: list[tuple[str, str]] = []
        self.dictionary: tuple[dict[str, object], str] | None = None

    def set_tracking_uri(self, _: str) -> None:
        pass

    def set_experiment(self, _: str) -> None:
        pass

    @contextmanager
    def start_run(self, run_name: str | None = None):
        del run_name
        yield FakeRun()

    def log_params(self, params: dict[str, object]) -> None:
        self.params = params

    def log_metrics(self, metrics: dict[str, float]) -> None:
        self.metrics = metrics

    def set_tags(self, tags: dict[str, str]) -> None:
        self.tags = tags

    def log_artifact(self, path: str, artifact_path: str) -> None:
        self.artifacts.append((path, artifact_path))

    def log_dict(self, dictionary: dict[str, object], path: str) -> None:
        self.dictionary = dictionary, path


def test_track_analysis_run_logs_parameters_metrics_and_artifacts(
    monkeypatch, tmp_path: Path
) -> None:
    fake_mlflow = FakeMlflow()
    monkeypatch.setattr(mlflow_tracking, "mlflow", fake_mlflow)
    summary_path = tmp_path / "summary.json"
    summary_path.write_text('{"frames_processed": 4}', encoding="utf-8")
    output_path = tmp_path / "annotated.mp4"
    output_path.touch()
    summary = AnalysisSummary(
        "input.mp4", str(output_path), "yolo11n.pt", 30.0, 5.0, 4,
        {"person": 9, "sports ball": 2}, 2.0, 3.0,
    )

    run_id = mlflow_tracking.track_analysis_run(
        summary,
        confidence_threshold=0.25,
        requested_sample_fps=5.0,
        summary_path=summary_path,
        annotated_video_path=output_path,
        tracking_directory=tmp_path / "tracking",
    )

    assert run_id == "run-123"
    assert fake_mlflow.params is not None
    assert fake_mlflow.params["model_name"] == "yolo11n.pt"
    assert fake_mlflow.metrics is not None
    assert fake_mlflow.metrics["detections_person"] == 9
    assert fake_mlflow.artifacts == [(str(summary_path), "run-output"), (str(output_path), "run-output")]
