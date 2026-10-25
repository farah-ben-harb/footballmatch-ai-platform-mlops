"""Promote the current candidate detector to the champion alias."""

import os

import mlflow
from mlflow import MlflowClient

TRACKING_URI = os.getenv(
    "FOOTBALLMATCH_MLFLOW_TRACKING_URI",
    "http://mlflow:5000",
)

MODEL_NAME = os.getenv(
    "FOOTBALLMATCH_MODEL_NAME",
    "FootballMatchYOLODetector",
)


def main() -> None:
    mlflow.set_tracking_uri(
        TRACKING_URI
    )

    client = MlflowClient()

    candidate = client.get_model_version_by_alias(
        MODEL_NAME,
        "candidate",
    )

    version = candidate.version

    print(
        "Candidate version:",
        version,
    )

    client.set_model_version_tag(
        name=MODEL_NAME,
        version=version,
        key="validation_status",
        value="approved",
    )

    client.set_registered_model_alias(
        name=MODEL_NAME,
        alias="champion",
        version=version,
    )

    champion = client.get_model_version_by_alias(
        MODEL_NAME,
        "champion",
    )

    print()
    print("=== PROMOTION ===")
    print(
        "Model:",
        MODEL_NAME,
    )
    print(
        "Version:",
        champion.version,
    )
    print(
        "Aliases:",
        champion.aliases,
    )
    print(
        "URI:",
        f"models:/{MODEL_NAME}@champion",
    )


if __name__ == "__main__":
    main()
