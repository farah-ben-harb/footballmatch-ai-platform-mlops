from pathlib import Path

import pytest

from footballmatch_api.cv import video


class FakeCapture:
    def __init__(self, properties: dict[int, float], opened: bool = True) -> None:
        self.properties = properties
        self.opened = opened
        self.released = False

    def isOpened(self) -> bool:
        return self.opened

    def get(self, property_id: int) -> float:
        return self.properties[property_id]

    def release(self) -> None:
        self.released = True


class FakeFrameCapture:
    def __init__(self, frames: list[str]) -> None:
        self.frames = iter(frames)
        self.released = False

    def isOpened(self) -> bool:
        return True

    def read(self) -> tuple[bool, str | None]:
        try:
            return True, next(self.frames)
        except StopIteration:
            return False, None

    def release(self) -> None:
        self.released = True


def test_read_video_metadata_returns_expected_values(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    source = tmp_path / "match.mp4"
    source.touch()
    capture = FakeCapture(
        {
            video.cv2.CAP_PROP_FPS: 25.0,
            video.cv2.CAP_PROP_FRAME_COUNT: 250.0,
            video.cv2.CAP_PROP_FRAME_WIDTH: 1280.0,
            video.cv2.CAP_PROP_FRAME_HEIGHT: 720.0,
        }
    )
    monkeypatch.setattr(video.cv2, "VideoCapture", lambda _: capture)

    metadata = video.read_video_metadata(source)

    assert metadata.path == source
    assert metadata.fps == 25.0
    assert metadata.frame_count == 250
    assert metadata.width == 1280
    assert metadata.height == 720
    assert metadata.duration_seconds == 10.0
    assert capture.released is True


def test_read_video_metadata_rejects_missing_file(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="does not exist"):
        video.read_video_metadata(tmp_path / "missing.mp4")


def test_create_sampling_plan_reduces_a_30_fps_video_to_about_5_fps() -> None:
    plan = video.create_sampling_plan(source_fps=30.0, target_fps=5.0)

    assert plan.frame_interval == 6
    assert plan.effective_fps == 5.0


def test_create_sampling_plan_never_skips_every_frame() -> None:
    plan = video.create_sampling_plan(source_fps=4.0, target_fps=5.0)

    assert plan.frame_interval == 1
    assert plan.effective_fps == 4.0


@pytest.mark.parametrize("source_fps,target_fps", [(0.0, 5.0), (30.0, 0.0)])
def test_create_sampling_plan_rejects_non_positive_fps(source_fps: float, target_fps: float) -> None:
    with pytest.raises(ValueError, match="must be greater than zero"):
        video.create_sampling_plan(source_fps=source_fps, target_fps=target_fps)


def test_iter_sampled_frames_yields_only_selected_frames(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    source = tmp_path / "match.mp4"
    source.touch()
    capture = FakeFrameCapture(["frame-0", "frame-1", "frame-2", "frame-3", "frame-4"])
    monkeypatch.setattr(video.cv2, "VideoCapture", lambda _: capture)

    frames = list(video.iter_sampled_frames(source, frame_interval=2))

    assert frames == [(0, "frame-0"), (2, "frame-2"), (4, "frame-4")]
    assert capture.released is True
