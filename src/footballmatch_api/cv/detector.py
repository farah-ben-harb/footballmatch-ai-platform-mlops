"""YOLO detector and multi-object tracking adapter."""

from dataclasses import dataclass
from typing import Any

from ultralytics import YOLO

FOOTBALL_RELEVANT_LABELS = frozenset(
    {
        "person",
        "sports ball",
    }
)


@dataclass(frozen=True, slots=True)
class Detection:
    """Model-independent object detection for one video frame."""

    class_id: int
    label: str
    confidence: float
    bounding_box: tuple[
        float,
        float,
        float,
        float,
    ]
    track_id: int | None = None


class YoloDetector:
    """YOLO detection and ByteTrack tracking adapter."""

    def __init__(
        self,
        model_name: str = "yolo11n.pt",
        confidence_threshold: float = 0.25,
        device: str = "cpu",
        tracker: str = "bytetrack.yaml",
        model: Any | None = None,
    ) -> None:
        if not 0 < confidence_threshold <= 1:
            raise ValueError(
                "Confidence threshold must be in the interval (0, 1]"
            )

        self.model_name = model_name
        self.confidence_threshold = confidence_threshold
        self.device = device
        self.tracker = tracker

        self._model = (
            model
            if model is not None
            else YOLO(model_name)
        )

    def detect(
        self,
        frame: Any,
        confidence_threshold: float | None = None,
    ) -> list[Detection]:
        """Run object detection without persistent tracking."""

        threshold = self._resolve_threshold(
            confidence_threshold
        )

        result = self._model.predict(
            source=frame,
            conf=threshold,
            device=self.device,
            verbose=False,
        )[0]

        return self._result_to_detections(
            result
        )

    def track(
        self,
        frame: Any,
        confidence_threshold: float | None = None,
    ) -> list[Detection]:
        """Track football-relevant objects across sequential frames."""

        threshold = self._resolve_threshold(
            confidence_threshold
        )

        result = self._model.track(
            source=frame,
            conf=threshold,
            device=self.device,
            tracker=self.tracker,
            persist=True,
            verbose=False,
        )[0]

        return self._result_to_detections(
            result
        )

    def reset_tracking(self) -> None:
        """Clear tracker state before processing a new video."""

        predictor = getattr(
            self._model,
            "predictor",
            None,
        )

        trackers = getattr(
            predictor,
            "trackers",
            None,
        )

        if not trackers:
            return

        for tracker in trackers:
            reset = getattr(
                tracker,
                "reset",
                None,
            )

            if callable(reset):
                reset()

    def _resolve_threshold(
        self,
        confidence_threshold: float | None,
    ) -> float:
        threshold = (
            confidence_threshold
            if confidence_threshold is not None
            else self.confidence_threshold
        )

        if not 0 < threshold <= 1:
            raise ValueError(
                "Confidence threshold must be in the interval (0, 1]"
            )

        return threshold

    def _result_to_detections(
        self,
        result: Any,
    ) -> list[Detection]:
        if result.boxes is None:
            return []

        detections: list[Detection] = []

        for box in result.boxes:
            class_id = int(
                box.cls[0]
            )

            label = str(
                self._model.names[class_id]
            )

            if label not in FOOTBALL_RELEVANT_LABELS:
                continue

            track_id = self._extract_track_id(
                box
            )

            detections.append(
                Detection(
                    class_id=class_id,
                    label=label,
                    confidence=float(
                        box.conf[0]
                    ),
                    bounding_box=tuple(
                        float(value)
                        for value in box.xyxy[
                            0
                        ].tolist()
                    ),
                    track_id=track_id,
                )
            )

        return detections

    @staticmethod
    def _extract_track_id(
        box: Any,
    ) -> int | None:
        """Extract an Ultralytics track ID when tracking is active."""

        box_id = getattr(
            box,
            "id",
            None,
        )

        if box_id is None:
            return None

        try:
            return int(
                box_id[0]
            )
        except (
            IndexError,
            TypeError,
        ):
            return None
