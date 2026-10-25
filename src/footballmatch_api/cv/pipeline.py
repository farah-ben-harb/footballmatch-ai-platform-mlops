"""Streaming computer-vision pipeline for football match videos."""

from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from time import perf_counter
from typing import Any, Protocol

import cv2

from footballmatch_api.cv.detector import Detection
from footballmatch_api.cv.video import (
    VideoProcessingError,
    create_sampling_plan,
    iter_sampled_frames,
    read_video_metadata,
)


class Detector(Protocol):
    """Minimum interface required by the video-analysis pipeline."""

    model_name: str

    def track(
        self,
        frame: Any,
        confidence_threshold: float | None = None,
    ) -> list[Detection]:
        """Return tracked detections for one sequential frame."""

    def reset_tracking(self) -> None:
        """Reset tracking state before processing a new video."""


@dataclass(frozen=True, slots=True)
class AnalysisSummary:
    """Observable result of one video-analysis run."""

    input_path: str
    output_path: str
    model_name: str
    source_fps: float
    effective_fps: float
    frames_processed: int
    detections_by_label: dict[str, int]
    inference_seconds: float
    total_seconds: float
    duration_seconds: float = 0.0
    unique_tracks_by_label: dict[str, int] = field(
        default_factory=dict
    )


def annotate_frame(
    frame: Any,
    detections: list[Detection],
) -> Any:
    """Draw labelled tracked detections on a copy of an OpenCV frame."""

    annotated = frame.copy()

    for detection in detections:
        left, top, right, bottom = (
            round(value)
            for value in detection.bounding_box
        )

        color = (
            (0, 255, 0)
            if detection.label == "person"
            else (0, 165, 255)
        )

        track_suffix = (
            f" #{detection.track_id}"
            if detection.track_id is not None
            else ""
        )

        label = (
            f"{detection.label}"
            f"{track_suffix} "
            f"{detection.confidence:.2f}"
        )

        cv2.rectangle(
            annotated,
            (left, top),
            (right, bottom),
            color,
            2,
        )

        cv2.putText(
            annotated,
            label,
            (left, max(20, top - 8)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            color,
            2,
            cv2.LINE_AA,
        )

    return annotated


def analyze_video(
    input_path: Path,
    output_path: Path,
    detector: Detector,
    target_fps: float = 5.0,
    confidence_threshold: float | None = None,
) -> AnalysisSummary:
    """Run tracked inference and write an annotated MP4 output video."""

    metadata = read_video_metadata(input_path)

    plan = create_sampling_plan(
        metadata.fps,
        target_fps,
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    writer = cv2.VideoWriter(
        str(output_path),
        cv2.VideoWriter_fourcc(*"mp4v"),
        plan.effective_fps,
        (metadata.width, metadata.height),
    )

    if not writer.isOpened():
        writer.release()

        raise VideoProcessingError(
            f"Unable to create output video: {output_path}"
        )

    started_at = perf_counter()
    inference_seconds = 0.0
    frames_processed = 0

    detection_counts: Counter[str] = Counter()

    # Example:
    # {
    #     "person": {1, 4, 7},
    #     "sports ball": {12},
    # }
    track_ids_by_label: dict[str, set[int]] = {}

    # Important: a new video must not inherit tracking state
    # from the previous video.
    detector.reset_tracking()

    try:
        for _, frame in iter_sampled_frames(
            input_path,
            plan.frame_interval,
        ):
            inference_started_at = perf_counter()

            detections = detector.track(
                frame,
                confidence_threshold=confidence_threshold,
            )

            inference_seconds += (
                perf_counter()
                - inference_started_at
            )

            writer.write(
                annotate_frame(
                    frame,
                    detections,
                )
            )

            frames_processed += 1

            detection_counts.update(
                detection.label
                for detection in detections
            )

            # Collect unique tracking IDs by object class.
            for detection in detections:
                if detection.track_id is None:
                    continue

                track_ids_by_label.setdefault(
                    detection.label,
                    set(),
                ).add(
                    detection.track_id
                )

    finally:
        writer.release()

    unique_tracks_by_label = {
        label: len(track_ids)
        for label, track_ids
        in track_ids_by_label.items()
    }

    return AnalysisSummary(
        input_path=str(input_path),
        output_path=str(output_path),
        model_name=detector.model_name,
        source_fps=metadata.fps,
        effective_fps=plan.effective_fps,
        frames_processed=frames_processed,
        detections_by_label=dict(detection_counts),
        inference_seconds=inference_seconds,
        total_seconds=perf_counter() - started_at,
        duration_seconds=metadata.duration_seconds,
        unique_tracks_by_label=unique_tracks_by_label,
    )
