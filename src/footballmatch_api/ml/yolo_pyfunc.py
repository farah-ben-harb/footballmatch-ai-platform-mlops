"""MLflow PyFunc wrapper around the football YOLO detector."""

import json
from typing import Any

import mlflow
import pandas as pd

FOOTBALL_RELEVANT_LABELS = frozenset(
    {
        "person",
        "sports ball",
    }
)


class FootballYoloPyFunc(mlflow.pyfunc.PythonModel):
    """Portable MLflow model wrapping YOLO inference."""

    def __init__(
        self,
        *,
        device: str = "cpu",
    ) -> None:
        self.device = device
        self.model: Any | None = None

    def load_context(
        self,
        context: mlflow.pyfunc.PythonModelContext,
    ) -> None:
        """Load YOLO weights packaged as an MLflow artifact."""

        from ultralytics import YOLO

        weights_path = context.artifacts[
            "weights"
        ]

        self.model = YOLO(
            weights_path
        )

    def predict(
        self,
        context: mlflow.pyfunc.PythonModelContext | None,
        model_input: pd.DataFrame,
        params: dict[str, Any] | None = None,
    ) -> pd.DataFrame:
        """Run YOLO detection for image paths supplied in a DataFrame."""

        del context, params

        if self.model is None:
            raise RuntimeError(
                "YOLO model is not loaded"
            )

        results: list[dict[str, object]] = []

        for row in model_input.to_dict(
            orient="records"
        ):
            image_path = str(
                row["image_path"]
            )

            confidence_threshold = float(
                row.get(
                    "confidence_threshold",
                    0.25,
                )
            )

            prediction = self.model.predict(
                source=image_path,
                conf=confidence_threshold,
                device=self.device,
                verbose=False,
            )[0]

            detections: list[
                dict[str, object]
            ] = []

            if prediction.boxes is not None:
                for box in prediction.boxes:
                    class_id = int(
                        box.cls[0]
                    )

                    label = str(
                        self.model.names[
                            class_id
                        ]
                    )

                    if (
                        label
                        not in FOOTBALL_RELEVANT_LABELS
                    ):
                        continue

                    detections.append(
                        {
                            "class_id": class_id,
                            "label": label,
                            "confidence": float(
                                box.conf[0]
                            ),
                            "bounding_box": [
                                float(value)
                                for value
                                in box.xyxy[
                                    0
                                ].tolist()
                            ],
                        }
                    )

            results.append(
                {
                    "image_path": image_path,
                    "detections_json": json.dumps(
                        detections
                    ),
                    "detection_count": len(
                        detections
                    ),
                }
            )

        return pd.DataFrame(
            results
        )
