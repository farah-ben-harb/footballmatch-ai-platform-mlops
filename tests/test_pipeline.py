from pathlib import Path

import pytest

from footballmatch_api.cv import pipeline
from footballmatch_api.cv.detector import Detection
from footballmatch_api.cv.video import (
    SamplingPlan,
    VideoMetadata,
    VideoProcessingError,
)


class FakeDetector:
    model_name = "fake-yolo.pt"

    def __init__(self) -> None:
        self.last_confidence_threshold: float | None = None
        self.reset_called = False

    def reset_tracking(self) -> None:
        self.reset_called = True

    def track(
        self,
        frame: str,
        confidence_threshold: float | None = None,
    ) -> list[Detection]:
        self.last_confidence_threshold = confidence_threshold

        if frame == "frame-0":
            return [
                Detection(
                    class_id=0,
                    label="person",
                    confidence=0.9,
                    bounding_box=(1.0, 2.0, 3.0, 4.0),
                    track_id=7,
                )
            ]

        if frame == "frame-10":
            return [
                Detection(
                    class_id=32,
                    label="sports ball",
                    confidence=0.8,
                    bounding_box=(5.0, 6.0, 7.0, 8.0),
                    track_id=12,
                )
            ]

        return []


class FakeWriter:
    def __init__(
        self,
        opened: bool = True,
    ) -> None:
        self.opened = opened
        self.frames: list[str] = []
        self.released = False

    def isOpened(self) -> bool:
        return self.opened

    def write(
        self,
        frame: str,
    ) -> None:
        self.frames.append(frame)

    def release(self) -> None:
        self.released = True


def test_analyze_video_uses_runtime_parameters(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    input_path = tmp_path / "match.mp4"

    output_path = (
        tmp_path
        / "artifacts"
        / "annotated.mp4"
    )

    metadata = VideoMetadata(
        input_path,
        30.0,
        300,
        1280,
        720,
        10.0,
    )

    writer = FakeWriter()
    detector = FakeDetector()
    sampling: dict[str, float] = {}

    monkeypatch.setattr(
        pipeline,
        "read_video_metadata",
        lambda _: metadata,
    )

    def fake_create_sampling_plan(
        source_fps: float,
        target_fps: float,
    ) -> SamplingPlan:
        sampling["source_fps"] = source_fps
        sampling["target_fps"] = target_fps

        return SamplingPlan(
            30.0,
            3.0,
            10,
            3.0,
        )

    monkeypatch.setattr(
        pipeline,
        "create_sampling_plan",
        fake_create_sampling_plan,
    )

    monkeypatch.setattr(
        pipeline,
        "iter_sampled_frames",
        lambda *_: iter(
            [
                (0, "frame-0"),
                (10, "frame-10"),
            ]
        ),
    )

    monkeypatch.setattr(
        pipeline.cv2,
        "VideoWriter",
        lambda *_: writer,
    )

    monkeypatch.setattr(
        pipeline,
        "annotate_frame",
        lambda frame, _: f"annotated-{frame}",
    )

    summary = pipeline.analyze_video(
        input_path,
        output_path,
        detector,
        target_fps=3.0,
        confidence_threshold=0.4,
    )

    assert sampling["target_fps"] == 3.0
    assert detector.last_confidence_threshold == 0.4
    assert detector.reset_called is True

    assert writer.frames == [
        "annotated-frame-0",
        "annotated-frame-10",
    ]

    assert writer.released is True

    assert summary.frames_processed == 2

    assert summary.detections_by_label == {
        "person": 1,
        "sports ball": 1,
    }

    assert summary.model_name == "fake-yolo.pt"

    assert summary.unique_tracks_by_label == {
        "person": 1,
        "sports ball": 1,
    }


def test_analyze_video_rejects_unavailable_output_writer(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    input_path = tmp_path / "match.mp4"
    output_path = tmp_path / "annotated.mp4"

    metadata = VideoMetadata(
        input_path,
        30.0,
        300,
        1280,
        720,
        10.0,
    )

    writer = FakeWriter(
        opened=False,
    )

    monkeypatch.setattr(
        pipeline,
        "read_video_metadata",
        lambda _: metadata,
    )

    monkeypatch.setattr(
        pipeline.cv2,
        "VideoWriter",
        lambda *_: writer,
    )

    with pytest.raises(
        VideoProcessingError,
        match="Unable to create",
    ):
        pipeline.analyze_video(
            input_path,
            output_path,
            FakeDetector(),
        )

    assert writer.released is True
