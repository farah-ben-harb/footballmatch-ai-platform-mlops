"""Load a registered detector from MLflow and perform smoke inference."""

import os
from pathlib import Path

import mlflow
import pandas as pd

TRACKING_URI = os.getenv(
    "FOOTBALLMATCH_MLFLOW_TRACKING_URI",
    "http://mlflow:5000",
)

MODEL_NAME = os.getenv(
    "FOOTBALLMATCH_MODEL_NAME",
    "FootballMatchYOLODetector",
)

MODEL_ALIAS = os.getenv(
    "FOOTBALLMATCH_MODEL_ALIAS",
    "candidate",
)

IMAGE_PATH = Path(
    os.getenv(
        "FOOTBALLMATCH_TEST_IMAGE",
        "/workspace/data/raw/registry-test-frame.jpg",
    )
)


def main() -> None:
    mlflow.set_tracking_uri(
        TRACKING_URI
    )

    model_uri = (
        f"models:/{MODEL_NAME}@{MODEL_ALIAS}"
    )

    print(
        "Loading:",
        model_uri,
    )

    if not IMAGE_PATH.exists():
        raise FileNotFoundError(
            IMAGE_PATH
        )

    model = mlflow.pyfunc.load_model(
        model_uri
    )

    model_input = pd.DataFrame(
        [
            {
                "image_path": str(
                    IMAGE_PATH
                ),
                "confidence_threshold": 0.30,
            }
        ]
    )

    prediction = model.predict(
        model_input
    )

    print()
    print("=== PREDICTION ===")
    print(
        prediction.to_string(
            index=False
        )
    )

    detection_count = int(
        prediction.iloc[0][
            "detection_count"
        ]
    )

    print()
    print(
        "Detection count:",
        detection_count,
    )

    if detection_count < 0:
        raise RuntimeError(
            "Invalid detection count"
        )

    print(
        "Registry smoke test: OK"
    )


if __name__ == "__main__":
    main()
