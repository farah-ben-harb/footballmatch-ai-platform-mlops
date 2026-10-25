"""YOLO object detection and ByteTrack multi-object tracking."""

import os
from collections.abc import Callable
from dataclasses import dataclass
from threading import Lock
from typing import Any

import mlflow
from ultralytics import YOLO

FOOTBALL_RELEVANT_LABELS = frozenset(
    {
        "person",
        "sports ball",
    }
)


@dataclass(frozen=True)
class Detection:
    """Single object detection."""

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
    """YOLO detector with optional MLflow Registry model loading."""

    def __init__(
        self,
        model_name: str = "yolo11n.pt",
        confidence_threshold: float = 0.25,
        device: str = "cpu",
        tracker: str = "bytetrack.yaml",
        model_uri: str | None = None,
        tracking_uri: str | None = None,
        model: Any | None = None,
        model_loader: Callable[[str], Any] | None = None,
    ) -> None:
        self.local_model_name = model_name

        self.model_uri = (
            model_uri
            or os.getenv(
                "FOOTBALLMATCH_DETECTOR_MODEL_URI"
            )
            or None
        )

        self.tracking_uri = (
            tracking_uri
            or os.getenv(
                "FOOTBALLMATCH_MLFLOW_TRACKING_URI"
            )
            or None
        )

        # Used in summaries and MLflow lineage.
        self.model_name = (
            self.model_uri
            or self.local_model_name
        )

        if not 0.0 < confidence_threshold <= 1.0:
            raise ValueError(
                "confidence_threshold must be in the interval (0, 1]"
            )

        self.confidence_threshold = (
            confidence_threshold
        )
        self.device = device
        self.tracker = tracker

        self._model: Any | None = model
        self._model_loader = model_loader
        self._model_lock = Lock()

    def detect(
        self,
        frame: Any,
        confidence_threshold: float | None = None,
    ) -> list[Detection]:
        """Run object detection on one frame."""

        model = self._get_model()

        threshold = self._resolve_threshold(
            confidence_threshold
        )

        result = model.predict(
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
        """Run YOLO + ByteTrack on one frame."""

        model = self._get_model()

        threshold = self._resolve_threshold(
            confidence_threshold
        )

        result = model.track(
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
        """Reset ByteTrack state between independent videos."""

        if self._model is None:
            return

        predictor = getattr(
            self._model,
            "predictor",
            None,
        )

        if predictor is None:
            return

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

    def _get_model(self) -> Any:
        """Lazy-load and reuse the detector model."""

        if self._model is not None:
            return self._model

        with self._model_lock:
            if self._model is None:
                self._model = (
                    self._load_model()
                )

        return self._model

    def _load_model(self) -> Any:
        """Load YOLO locally or from MLflow Model Registry."""

        if not self.model_uri:
            return YOLO(
                self.local_model_name
            )

        if self._model_loader is not None:
            loaded_model = self._model_loader(
                self.model_uri
            )
        else:
            if self.tracking_uri:
                mlflow.set_tracking_uri(
                    self.tracking_uri
                )
                mlflow.set_registry_uri(
                    self.tracking_uri
                )

            loaded_model = (
                mlflow.pyfunc.load_model(
                    self.model_uri
                )
            )

        python_model = (
            loaded_model.unwrap_python_model()
        )

        model = getattr(
            python_model,
            "model",
            None,
        )

        if model is None:
            raise RuntimeError(
                "The registered MLflow model "
                "does not expose a loaded YOLO model"
            )

        if not hasattr(
            model,
            "track",
        ):
            raise RuntimeError(
                "The registered model does not "
                "support YOLO tracking"
            )

        return model

    def _result_to_detections(
        self,
        result: Any,
    ) -> list[Detection]:
        """Convert an Ultralytics result into domain detections."""

        if result.boxes is None:
            return []

        model = self._get_model()

        detections: list[Detection] = []

        for box in result.boxes:
            class_id = int(
                box.cls[0]
            )

            label = str(
                model.names[
                    class_id
                ]
            )

            if (
                label
                not in FOOTBALL_RELEVANT_LABELS
            ):
                continue

            coordinates = (
                box.xyxy[0].tolist()
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
                        for value
                        in coordinates
                    ),
                    track_id=(
                        self._extract_track_id(
                            box
                        )
                    ),
                )
            )

        return detections

    @staticmethod
    def _extract_track_id(
        box: Any,
    ) -> int | None:
        """Extract ByteTrack ID when available."""

        track_ids = getattr(
            box,
            "id",
            None,
        )

        if track_ids is None:
            return None

        if len(track_ids) == 0:
            return None

        return int(
            track_ids[0]
        )

    def _resolve_threshold(
        self,
        confidence_threshold: float | None,
    ) -> float:
        """Resolve per-request or default confidence threshold."""

        if confidence_threshold is None:
            return self.confidence_threshold

        return confidence_threshold
