from pathlib import Path

import pytest

from footballmatch_api.cv import pipeline
from footballmatch_api.cv.detector import Detection
from footballmatch_api.cv.video import SamplingPlan, VideoMetadata, VideoProcessingError


class FakeDetector:
    model_name = "fake-yolo.pt"

    def detect(self, frame: str) -> list[Detection]:
        if frame == "frame-0":
            return [Detection(0, "person", 0.9, (1.0, 2.0, 3.0, 4.0))]
        return [Detection(32, "sports ball", 0.8, (5.0, 6.0, 7.0, 8.0))]


class FakeWriter:
    def __init__(self, opened: bool = True) -> None:
        self.opened = opened
        self.frames: list[str] = []
        self.released = False

    def isOpened(self) -> bool:
        return self.opened

    def write(self, frame: str) -> None:
        self.frames.append(frame)

    def release(self) -> None:
        self.released = True


def test_analyze_video_writes_sampled_annotated_frames(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    input_path = tmp_path / "match.mp4"
    output_path = tmp_path / "artifacts" / "annotated.mp4"
    metadata = VideoMetadata(input_path, 30.0, 300, 1280, 720, 10.0)
    writer = FakeWriter()
    monkeypatch.setattr(pipeline, "read_video_metadata", lambda _: metadata)
    monkeypatch.setattr(
        pipeline,
        "create_sampling_plan",
        lambda *_: SamplingPlan(30.0, 5.0, 6, 5.0),
    )
    monkeypatch.setattr(
        pipeline,
        "iter_sampled_frames",
        lambda *_: iter([(0, "frame-0"), (6, "frame-6")]),
    )
    monkeypatch.setattr(pipeline.cv2, "VideoWriter", lambda *_: writer)
    monkeypatch.setattr(pipeline, "annotate_frame", lambda frame, _: f"annotated-{frame}")

    summary = pipeline.analyze_video(input_path, output_path, FakeDetector())

    assert writer.frames == ["annotated-frame-0", "annotated-frame-6"]
    assert writer.released is True
    assert summary.frames_processed == 2
    assert summary.detections_by_label == {"person": 1, "sports ball": 1}
    assert summary.model_name == "fake-yolo.pt"


def test_analyze_video_rejects_unavailable_output_writer(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    input_path = tmp_path / "match.mp4"
    output_path = tmp_path / "annotated.mp4"
    metadata = VideoMetadata(input_path, 30.0, 300, 1280, 720, 10.0)
    writer = FakeWriter(opened=False)
    monkeypatch.setattr(pipeline, "read_video_metadata", lambda _: metadata)
    monkeypatch.setattr(pipeline.cv2, "VideoWriter", lambda *_: writer)

    with pytest.raises(VideoProcessingError, match="Unable to create"):
        pipeline.analyze_video(input_path, output_path, FakeDetector())

    assert writer.released is True
