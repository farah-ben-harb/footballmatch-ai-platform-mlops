"""Video input validation and metadata extraction."""

from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import cv2


class VideoProcessingError(RuntimeError):
    """Raised when a video file cannot provide valid processing metadata."""


@dataclass(frozen=True, slots=True)
class VideoMetadata:
    """Properties required to plan a video-analysis run."""

    path: Path
    fps: float
    frame_count: int
    width: int
    height: int
    duration_seconds: float


@dataclass(frozen=True, slots=True)
class SamplingPlan:
    """A deterministic plan for reducing video frames before inference."""

    source_fps: float
    target_fps: float
    frame_interval: int
    effective_fps: float


def create_sampling_plan(source_fps: float, target_fps: float) -> SamplingPlan:
    """Calculate how often the pipeline should process a source frame."""
    if source_fps <= 0:
        raise ValueError("Source FPS must be greater than zero")
    if target_fps <= 0:
        raise ValueError("Target FPS must be greater than zero")

    frame_interval = max(1, round(source_fps / target_fps))
    return SamplingPlan(
        source_fps=source_fps,
        target_fps=target_fps,
        frame_interval=frame_interval,
        effective_fps=source_fps / frame_interval,
    )


def iter_sampled_frames(path: Path, frame_interval: int) -> Iterator[tuple[int, Any]]:
    """Yield selected frames without loading the entire video into memory."""
    if frame_interval < 1:
        raise ValueError("Frame interval must be at least one")

    capture = cv2.VideoCapture(str(path))
    if not capture.isOpened():
        capture.release()
        raise VideoProcessingError(f"Unable to open video: {path}")

    frame_index = 0
    try:
        while True:
            success, frame = capture.read()
            if not success:
                break
            if frame_index % frame_interval == 0:
                yield frame_index, frame
            frame_index += 1
    finally:
        capture.release()


def read_video_metadata(path: Path) -> VideoMetadata:
    """Open a video once and return the metadata needed by the pipeline."""
    if not path.is_file():
        raise FileNotFoundError(f"Video file does not exist: {path}")

    capture = cv2.VideoCapture(str(path))
    if not capture.isOpened():
        capture.release()
        raise VideoProcessingError(f"Unable to open video: {path}")

    try:
        fps = float(capture.get(cv2.CAP_PROP_FPS))
        frame_count = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    finally:
        capture.release()

    if fps <= 0 or frame_count <= 0 or width <= 0 or height <= 0:
        raise VideoProcessingError(f"Video has invalid metadata: {path}")

    return VideoMetadata(
        path=path,
        fps=fps,
        frame_count=frame_count,
        width=width,
        height=height,
        duration_seconds=frame_count / fps,
    )
