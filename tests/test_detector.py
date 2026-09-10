from typing import ClassVar

import pytest

from footballmatch_api.cv.detector import Detection, YoloDetector


class FakeTensor:
    def __init__(self, values: list[float]) -> None:
        self.values = values

    def __getitem__(self, index: int) -> float:
        value = self.values[index]
        return value

    def tolist(self) -> list[float]:
        return self.values


class FakeBox:
    def __init__(
        self,
        class_id: int,
        confidence: float,
        coordinates: list[float],
    ) -> None:
        self.cls = FakeTensor([float(class_id)])
        self.conf = FakeTensor([confidence])
        self.xyxy = [FakeTensor(coordinates)]


class FakeResult:
    def __init__(self, boxes: list[FakeBox] | None) -> None:
        self.boxes = boxes


class FakeModel:
    names: ClassVar[dict[int, str]] = {0: "person", 32: "sports ball", 1: "bicycle"}

    def __init__(self, boxes: list[FakeBox] | None) -> None:
        self.boxes = boxes
        self.predict_arguments: dict[str, object] | None = None

    def predict(self, **kwargs: object) -> list[FakeResult]:
        self.predict_arguments = kwargs
        return [FakeResult(self.boxes)]


def test_detector_returns_only_football_relevant_classes() -> None:
    model = FakeModel(
        [
            FakeBox(class_id=0, confidence=0.91, coordinates=[10, 20, 30, 40]),
            FakeBox(class_id=1, confidence=0.88, coordinates=[50, 60, 70, 80]),
            FakeBox(class_id=32, confidence=0.65, coordinates=[90, 100, 110, 120]),
        ]
    )
    detector = YoloDetector(confidence_threshold=0.5, model=model)

    detections = detector.detect(frame="frame")

    assert detections == [
        Detection(0, "person", 0.91, (10.0, 20.0, 30.0, 40.0)),
        Detection(32, "sports ball", 0.65, (90.0, 100.0, 110.0, 120.0)),
    ]
    assert model.predict_arguments == {
        "source": "frame",
        "conf": 0.5,
        "device": "cpu",
        "verbose": False,
    }


def test_detector_returns_no_detections_when_yolo_returns_no_boxes() -> None:
    detector = YoloDetector(model=FakeModel(boxes=None))

    assert detector.detect(frame="frame") == []


@pytest.mark.parametrize("confidence_threshold", [0.0, -0.1, 1.1])
def test_detector_rejects_invalid_confidence_threshold(confidence_threshold: float) -> None:
    with pytest.raises(ValueError, match="interval"):
        YoloDetector(confidence_threshold=confidence_threshold, model=FakeModel(boxes=[]))
