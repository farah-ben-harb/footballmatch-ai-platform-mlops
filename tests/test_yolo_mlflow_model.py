import json
from typing import ClassVar

import pandas as pd

from footballmatch_api.ml.yolo_pyfunc import (
    FootballYoloPyFunc,
)


class FakeTensor:
    def __init__(
        self,
        values: list[float],
    ) -> None:
        self.values = values

    def __getitem__(
        self,
        index: int,
    ) -> float:
        return self.values[index]

    def tolist(
        self,
    ) -> list[float]:
        return self.values


class FakeBox:
    def __init__(
        self,
        class_id: int,
        confidence: float,
        coordinates: list[float],
    ) -> None:
        self.cls = FakeTensor(
            [float(class_id)]
        )

        self.conf = FakeTensor(
            [confidence]
        )

        self.xyxy = [
            FakeTensor(
                coordinates
            )
        ]


class FakeResult:
    def __init__(
        self,
        boxes: list[FakeBox],
    ) -> None:
        self.boxes = boxes


class FakeModel:
    names: ClassVar[
        dict[int, str]
    ] = {
        0: "person",
        1: "bicycle",
        32: "sports ball",
    }

    def __init__(self) -> None:
        self.last_predict_arguments = {}

    def predict(
        self,
        **kwargs,
    ) -> list[FakeResult]:
        self.last_predict_arguments = kwargs

        return [
            FakeResult(
                [
                    FakeBox(
                        0,
                        0.91,
                        [10, 20, 30, 40],
                    ),
                    FakeBox(
                        1,
                        0.88,
                        [50, 60, 70, 80],
                    ),
                    FakeBox(
                        32,
                        0.67,
                        [90, 100, 110, 120],
                    ),
                ]
            )
        ]


def test_mlflow_yolo_pyfunc_predict() -> None:
    model = FootballYoloPyFunc(
        device="cpu"
    )

    fake_model = FakeModel()
    model.model = fake_model

    model_input = pd.DataFrame(
        [
            {
                "image_path": "/tmp/frame.jpg",
                "confidence_threshold": 0.4,
            }
        ]
    )

    result = model.predict(
        None,
        model_input,
    )

    assert result.iloc[0][
        "detection_count"
    ] == 2

    detections = json.loads(
        result.iloc[0][
            "detections_json"
        ]
    )

    assert [
        detection["label"]
        for detection in detections
    ] == [
        "person",
        "sports ball",
    ]

    assert (
        fake_model.last_predict_arguments[
            "conf"
        ]
        == 0.4
    )

    assert (
        fake_model.last_predict_arguments[
            "device"
        ]
        == "cpu"
    )
