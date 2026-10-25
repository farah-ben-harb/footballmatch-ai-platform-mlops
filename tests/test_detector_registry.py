from typing import ClassVar

from footballmatch_api.cv.detector import (
    YoloDetector,
)


class FakeTensor:
    def __init__(
        self,
        values,
    ) -> None:
        self.values = values

    def __getitem__(
        self,
        index,
    ):
        return self.values[index]

    def __len__(self) -> int:
        return len(self.values)

    def tolist(self):
        return self.values


class FakeBox:
    def __init__(self) -> None:
        self.cls = FakeTensor([0.0])
        self.conf = FakeTensor([0.93])

        self.xyxy = [
            FakeTensor(
                [
                    10.0,
                    20.0,
                    100.0,
                    200.0,
                ]
            )
        ]

        self.id = FakeTensor([17.0])


class FakeResult:
    def __init__(self) -> None:
        self.boxes = [
            FakeBox()
        ]


class FakeYolo:
    names: ClassVar[
        dict[int, str]
    ] = {
        0: "person",
    }

    def __init__(self) -> None:
        self.last_track_arguments = None

    def track(
        self,
        **kwargs,
    ):
        self.last_track_arguments = kwargs

        return [
            FakeResult()
        ]


class FakePythonModel:
    def __init__(
        self,
        model,
    ) -> None:
        self.model = model


class FakeMlflowModel:
    def __init__(
        self,
        model,
    ) -> None:
        self.python_model = FakePythonModel(
            model
        )

    def unwrap_python_model(self):
        return self.python_model


def test_detector_loads_registry_model_and_tracks() -> None:
    fake_yolo = FakeYolo()

    loaded_uris = []

    def fake_load_model(
        model_uri,
    ):
        loaded_uris.append(
            model_uri
        )

        return FakeMlflowModel(
            fake_yolo
        )

    detector = YoloDetector(
        model_uri=(
            "models:/"
            "FootballMatchYOLODetector"
            "@champion"
        ),
        tracking_uri="http://mlflow:5000",
        model_loader=fake_load_model,
    )

    detections = detector.track(
        frame="fake-frame",
        confidence_threshold=0.40,
    )

    assert loaded_uris == [
        (
            "models:/"
            "FootballMatchYOLODetector"
            "@champion"
        )
    ]

    assert len(detections) == 1

    detection = detections[0]

    assert detection.label == "person"
    assert detection.track_id == 17
    assert detection.confidence == 0.93

    assert (
        fake_yolo.last_track_arguments[
            "tracker"
        ]
        == "bytetrack.yaml"
    )

    assert (
        fake_yolo.last_track_arguments[
            "persist"
        ]
        is True
    )

    assert (
        fake_yolo.last_track_arguments[
            "conf"
        ]
        == 0.40
    )
