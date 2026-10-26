"""Convert a FootballMatch analysis JSON response into a RAG document."""

import argparse
import json
from pathlib import Path
from typing import Any

from footballmatch_api.rag.document_builder import (
    build_analysis_document,
    document_to_json,
)


def load_payload(
    path: Path,
) -> dict[str, Any]:
    return json.loads(
        path.read_text()
    )


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "input",
        type=Path,
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=Path(
            "/tmp/footballmatch-rag-document.json"
        ),
    )

    args = parser.parse_args()

    payload = load_payload(
        args.input
    )

    summary = payload.get(
        "result",
        payload,
    )

    job_id = str(
        payload.get(
            "id",
            payload.get(
                "job_id",
                "unknown",
            ),
        )
    )

    mlflow_run_id = payload.get(
        "mlflow_run_id"
    )

    document = build_analysis_document(
        summary,
        job_id=job_id,
        mlflow_run_id=mlflow_run_id,
    )

    args.output.write_text(
        document_to_json(
            document
        )
    )

    print(
        "RAG document:",
        args.output,
    )

    print(
        "Chunks:",
        len(document.chunks),
    )

    print(
        "SHA256:",
        document.content_sha256,
    )


if __name__ == "__main__":
    main()
