"""Pretrained object-detector adapter for football video analysis."""

from dataclasses import dataclass
from typing import Any

from ultralytics import YOLO

FOOTBALL_RELEVANT_LABELS = frozenset({"person", "sports ball"})


@dataclass(frozen=True, slots=True)
class Detection:
    """A model-independent object detection for one video frame."""

    class_id: int
    label: str
    confidence: float
    bounding_box: tuple[float, float, float, float]


class YoloDetector:
    """Adapt a pretrained YOLO model to the project's detection contract."""

    def __init__(
        self,
        model_name: str = "yolo11n.pt",
        confidence_threshold: float = 0.25,
        device: str = "cpu",
        model: Any | None = None,
    ) -> None:
        if not 0 < confidence_threshold <= 1:
            raise ValueError(
                "Confidence threshold must be in the interval (0, 1]"
            )

        self.model_name = model_name
        self.confidence_threshold = confidence_threshold
        self.device = device
        self._model = model if model is not None else YOLO(model_name)

    def detect(
        self,
        frame: Any,
        confidence_threshold: float | None = None,
    ) -> list[Detection]:
        """Predict football-relevant objects in one OpenCV frame."""

        threshold = (
            confidence_threshold
            if confidence_threshold is not None
            else self.confidence_threshold
        )

        if not 0 < threshold <= 1:
            raise ValueError(
                "Confidence threshold must be in the interval (0, 1]"
            )

        result = self._model.predict(
            source=frame,
            conf=threshold,
            device=self.device,
            verbose=False,
        )[0]

        if result.boxes is None:
            return []

        detections: list[Detection] = []

        for box in result.boxes:
            class_id = int(box.cls[0])
            label = str(self._model.names[class_id])

            if label not in FOOTBALL_RELEVANT_LABELS:
                continue

            detections.append(
                Detection(
                    class_id=class_id,
                    label=label,
                    confidence=float(box.conf[0]),
                    bounding_box=tuple(
                        float(value)
                        for value in box.xyxy[0].tolist()
                    ),
                )
            )

        return detections
