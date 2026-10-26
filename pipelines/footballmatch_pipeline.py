"""Kubeflow Pipeline for FootballMatch AI Platform."""

from kfp import dsl

REQUESTS_REQUIREMENT = "requests>=2.32,<3"


@dsl.component(
    base_image="python:3.10-slim",
    packages_to_install=[REQUESTS_REQUIREMENT],
)
def submit_analysis(
    api_url: str,
    video_url: str,
    confidence_threshold: float = 0.25,
    sample_fps: float = 2.0,
    upload_field: str = "file",
) -> str:
    """Download a video and submit it to FootballMatch FastAPI."""

    import tempfile

    import requests

    video_response = requests.get(
        video_url,
        timeout=120,
    )
    video_response.raise_for_status()

    with tempfile.NamedTemporaryFile(
        suffix=".mp4",
    ) as video_file:
        video_file.write(
            video_response.content
        )
        video_file.flush()

        with open(
            video_file.name,
            "rb",
        ) as handle:
            response = requests.post(
                (
                    api_url.rstrip("/")
                    + "/analyze"
                ),
                files={
                    upload_field: (
                        "match.mp4",
                        handle,
                        "video/mp4",
                    )
                },
                data={
                    "confidence_threshold": str(
                        confidence_threshold
                    ),
                    "sample_fps": str(
                        sample_fps
                    ),
                },
                timeout=120,
            )

    response.raise_for_status()

    payload = response.json()

    job_id = (
        payload.get("id")
        or payload.get("job_id")
    )

    if not job_id:
        raise RuntimeError(
            "Analysis API did not return a job ID"
        )

    print(
        "Submitted analysis job:",
        job_id,
    )

    return str(job_id)


@dsl.component(
    base_image="python:3.10-slim",
    packages_to_install=[REQUESTS_REQUIREMENT],
)
def wait_for_analysis(
    api_url: str,
    job_id: str,
    poll_seconds: int = 2,
    max_attempts: int = 300,
) -> str:
    """Poll the asynchronous analysis job until completion."""

    import json
    import time

    import requests

    endpoint = (
        api_url.rstrip("/")
        + "/jobs/"
        + job_id
    )

    for attempt in range(
        1,
        max_attempts + 1,
    ):
        response = requests.get(
            endpoint,
            timeout=30,
        )
        response.raise_for_status()

        payload = response.json()

        status = payload.get(
            "status"
        )

        print(
            "Attempt",
            attempt,
            "status:",
            status,
        )

        if status == "completed":
            return json.dumps(
                payload
            )

        if status == "failed":
            raise RuntimeError(
                "Football analysis failed: "
                + str(
                    payload.get(
                        "error",
                        "unknown error",
                    )
                )
            )

        time.sleep(
            poll_seconds
        )

    raise TimeoutError(
        "Analysis job did not complete "
        "within the configured polling window"
    )


@dsl.component(
    base_image="python:3.10-slim",
)
def validate_analysis(
    analysis_payload: str,
) -> str:
    """Validate the completed FootballMatch result."""

    import json

    payload = json.loads(
        analysis_payload
    )

    if payload.get("status") != "completed":
        raise RuntimeError(
            "Expected a completed analysis"
        )

    result = payload.get(
        "result"
    )

    if not result:
        raise RuntimeError(
            "Completed analysis has no result"
        )

    summary = {
        "job_id": (
            payload.get("id")
            or payload.get("job_id")
        ),
        "status": payload.get(
            "status"
        ),
        "mlflow_run_id": payload.get(
            "mlflow_run_id"
        ),
        "frames_processed": result.get(
            "frames_processed"
        ),
    }

    print(
        json.dumps(
            summary,
            indent=2,
        )
    )

    return json.dumps(
        summary
    )


@dsl.component(
    base_image="python:3.10-slim",
    packages_to_install=[REQUESTS_REQUIREMENT],
)
def validate_rag_indexing(
    api_url: str,
    job_id: str,
    question: str,
    limit: int = 3,
    poll_seconds: int = 2,
    max_attempts: int = 30,
) -> str:
    """Verify that the new analysis became searchable through RAG."""

    import json
    import time

    import requests

    endpoint = (
        api_url.rstrip("/")
        + "/rag/ask"
    )

    for attempt in range(
        1,
        max_attempts + 1,
    ):
        response = requests.post(
            endpoint,
            json={
                "question": question,
                "limit": limit,
            },
            timeout=180,
        )

        response.raise_for_status()

        payload = response.json()

        sources = payload.get(
            "sources",
            [],
        )

        matching_sources = [
            source
            for source in sources
            if str(
                source.get("job_id")
            )
            == str(job_id)
        ]

        if matching_sources:
            print(
                "RAG validation succeeded "
                "for job:",
                job_id,
            )

            print(
                "Answer:",
                payload.get(
                    "answer"
                ),
            )

            return json.dumps(
                payload
            )

        print(
            "RAG document not ready yet. "
            "Attempt:",
            attempt,
        )

        time.sleep(
            poll_seconds
        )

    raise RuntimeError(
        "The completed analysis did not "
        "become searchable in RAG"
    )


@dsl.pipeline(
    name="footballmatch-ai-platform",
    description=(
        "End-to-end orchestration of FootballMatch "
        "video analysis, MLflow tracking and RAG validation."
    ),
)
def footballmatch_pipeline(
    api_url: str,
    video_url: str,
    confidence_threshold: float = 0.25,
    sample_fps: float = 2.0,
    upload_field: str = "file",
    rag_question: str = (
        "How many player tracks were detected?"
    ),
    rag_limit: int = 3,
) -> None:
    """Orchestrate one complete FootballMatch analysis."""

    submit_task = submit_analysis(
        api_url=api_url,
        video_url=video_url,
        confidence_threshold=confidence_threshold,
        sample_fps=sample_fps,
        upload_field=upload_field,
    )

    submit_task.set_caching_options(
        False
    )

    wait_task = wait_for_analysis(
        api_url=api_url,
        job_id=submit_task.output,
    )

    wait_task.set_caching_options(
        False
    )

    validation_task = validate_analysis(
        analysis_payload=wait_task.output,
    )

    validation_task.set_caching_options(
        False
    )

    rag_task = validate_rag_indexing(
        api_url=api_url,
        job_id=submit_task.output,
        question=rag_question,
        limit=rag_limit,
    )

    rag_task.after(
        validation_task
    )

    rag_task.set_caching_options(
        False
    )
