from io import BytesIO
from pathlib import Path

from prometheus_client import REGISTRY

from footballmatch_api.cv.pipeline import AnalysisSummary
from footballmatch_api.services import analysis_jobs


class FakeDetector:
    confidence_threshold = 0.25


def test_save_upload_rejects_an_unsupported_extension(
    tmp_path: Path,
) -> None:
    service = analysis_jobs.AnalysisJobService(
        tmp_path,
        100,
    )

    try:
        service.save_upload(
            "match.exe",
            BytesIO(b"not-a-video"),
        )
    except ValueError as error:
        assert "Only MP4" in str(error)
    else:
        raise AssertionError(
            "Expected unsupported upload to be rejected"
        )


def test_run_uses_job_parameters_and_reuses_detector(
    monkeypatch,
    tmp_path: Path,
) -> None:
    detector_calls = 0
    captured: dict[str, object] = {}

    def detector_factory() -> FakeDetector:
        nonlocal detector_calls
        detector_calls += 1
        return FakeDetector()

    def fake_pipeline(
        input_path: Path,
        output_path: Path,
        detector: FakeDetector,
        *,
        target_fps: float = 5.0,
        confidence_threshold: float | None = None,
    ) -> AnalysisSummary:
        del detector

        captured["target_fps"] = target_fps
        captured["confidence_threshold"] = confidence_threshold

        output_path.touch()

        return AnalysisSummary(
            str(input_path),
            str(output_path),
            "fake-yolo",
            30.0,
            target_fps,
            2,
            {},
            1.0,
            2.0,
        )

    def fake_track_analysis_run(
        _summary,
        **kwargs,
    ) -> str:
        captured["mlflow_confidence"] = kwargs[
            "confidence_threshold"
        ]
        captured["mlflow_sample_fps"] = kwargs[
            "requested_sample_fps"
        ]

        return "run-abc"

    monkeypatch.setattr(
        analysis_jobs,
        "track_analysis_run",
        fake_track_analysis_run,
    )

    service = analysis_jobs.AnalysisJobService(
        tmp_path,
        100,
        detector_factory=detector_factory,
        pipeline=fake_pipeline,
    )

    job = service.save_upload(
        "match.mp4",
        BytesIO(b"video"),
        confidence_threshold=0.4,
        sample_fps=3.0,
    )

    before = REGISTRY.get_sample_value(
        "footballmatch_video_analysis_duration_seconds_count"
    ) or 0
    service.run(job.id)
    after = REGISTRY.get_sample_value(
        "footballmatch_video_analysis_duration_seconds_count"
    )

    assert after == before + 1

    completed = service.get(job.id)

    assert completed is not None
    assert completed.status == "completed"
    assert completed.mlflow_run_id == "run-abc"
    assert completed.result is not None

    assert detector_calls == 1

    assert captured["target_fps"] == 3.0
    assert captured["confidence_threshold"] == 0.4

    assert captured["mlflow_confidence"] == 0.4
    assert captured["mlflow_sample_fps"] == 3.0


def test_run_records_pipeline_failures(
    monkeypatch,
    tmp_path: Path,
) -> None:
    def failing_pipeline(
        *_args,
        **_kwargs,
    ):
        raise RuntimeError("bad video")

    monkeypatch.setattr(
        analysis_jobs,
        "track_analysis_run",
        lambda *_args, **_kwargs: "unused",
    )

    service = analysis_jobs.AnalysisJobService(
        tmp_path,
        100,
        detector_factory=FakeDetector,
        pipeline=failing_pipeline,
    )

    job = service.save_upload(
        "match.mp4",
        BytesIO(b"video"),
    )

    before = REGISTRY.get_sample_value(
        "footballmatch_video_analysis_duration_seconds_count"
    ) or 0
    service.run(job.id)
    after = REGISTRY.get_sample_value(
        "footballmatch_video_analysis_duration_seconds_count"
    )

    assert after == before + 1

    failed = service.get(job.id)

    assert failed is not None
    assert failed.status == "failed"
    assert failed.error == "bad video"
