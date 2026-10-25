"""Log and register the FootballMatch YOLO detector in MLflow."""

import os
from importlib.metadata import version
from pathlib import Path

import mlflow
from mlflow import MlflowClient
from mlflow.models import ModelSignature
from mlflow.types.schema import ColSpec, Schema
from ultralytics import YOLO

from footballmatch_api.ml.yolo_pyfunc import (
    FootballYoloPyFunc,
)

TRACKING_URI = os.getenv(
    "FOOTBALLMATCH_MLFLOW_TRACKING_URI",
    "http://mlflow:5000",
)

EXPERIMENT_NAME = os.getenv(
    "FOOTBALLMATCH_MLFLOW_EXPERIMENT_NAME",
    "football-video-analysis",
)

REGISTERED_MODEL_NAME = (
    "FootballMatchYOLODetector"
)

MODEL_ALIAS = "candidate"


def installed_version(
    package: str,
) -> str:
    return version(package)


def ensure_weights() -> Path:
    """Ensure YOLO weights exist locally before MLflow packages them."""

    weights_directory = Path(
        "/tmp/footballmatch-model"
    )

    weights_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    old_directory = Path.cwd()

    try:
        os.chdir(
            weights_directory
        )

        model = YOLO(
            "yolo11n.pt"
        )

        checkpoint = Path(
            model.ckpt_path
        )

        if not checkpoint.is_absolute():
            checkpoint = (
                weights_directory
                / checkpoint
            )

        return checkpoint.resolve()

    finally:
        os.chdir(
            old_directory
        )


def main() -> None:
    mlflow.set_tracking_uri(
        TRACKING_URI
    )

    mlflow.set_experiment(
        EXPERIMENT_NAME
    )

    weights_path = ensure_weights()

    print(
        "Weights:",
        weights_path,
    )

    input_schema = Schema(
        [
            ColSpec(
                "string",
                "image_path",
            ),
            ColSpec(
                "double",
                "confidence_threshold",
            ),
        ]
    )

    output_schema = Schema(
        [
            ColSpec(
                "string",
                "image_path",
            ),
            ColSpec(
                "string",
                "detections_json",
            ),
            ColSpec(
                "long",
                "detection_count",
            ),
        ]
    )

    signature = ModelSignature(
        inputs=input_schema,
        outputs=output_schema,
    )

    requirements = [
        f"mlflow=={installed_version('mlflow')}",
        f"pandas=={installed_version('pandas')}",
        f"numpy=={installed_version('numpy')}",
        f"ultralytics=={installed_version('ultralytics')}",
        f"torch=={installed_version('torch')}",
        f"torchvision=={installed_version('torchvision')}",
    ]

    with mlflow.start_run(
        run_name="register-yolo-detector",
    ) as run:
        mlflow.log_params(
            {
                "model_name": "yolo11n.pt",
                "device": "cpu",
                "model_role": "object-detector",
            }
        )

        mlflow.set_tags(
            {
                "model_framework": "ultralytics-yolo",
                "registry_candidate": "true",
                "workload": "football-video-analysis",
            }
        )

        mlflow.pyfunc.log_model(
            artifact_path="detector-model",
            python_model=FootballYoloPyFunc(
                device="cpu"
            ),
            artifacts={
                "weights": str(
                    weights_path
                )
            },
            code_paths=[
                "src",
            ],
            signature=signature,
            pip_requirements=requirements,
        )

        run_id = run.info.run_id

    model_uri = (
        f"runs:/{run_id}/detector-model"
    )

    registered = mlflow.register_model(
        model_uri=model_uri,
        name=REGISTERED_MODEL_NAME,
    )

    client = MlflowClient()

    client.set_registered_model_alias(
        name=REGISTERED_MODEL_NAME,
        alias=MODEL_ALIAS,
        version=registered.version,
    )

    client.set_model_version_tag(
        name=REGISTERED_MODEL_NAME,
        version=registered.version,
        key="validation_status",
        value="candidate",
    )

    print()
    print("=== REGISTERED MODEL ===")
    print(
        "Name:",
        REGISTERED_MODEL_NAME,
    )
    print(
        "Version:",
        registered.version,
    )
    print(
        "Alias:",
        MODEL_ALIAS,
    )
    print(
        "Run ID:",
        run_id,
    )

    print(
        "URI:",
        (
            f"models:/"
            f"{REGISTERED_MODEL_NAME}"
            f"@{MODEL_ALIAS}"
        ),
    )


if __name__ == "__main__":
    main()
