"""Build RAG documents from football video analysis results."""

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class RagChunk:
    """Semantic chunk ready for embedding."""

    index: int
    content: str
    metadata: dict[str, Any] = field(
        default_factory=dict
    )


@dataclass(frozen=True)
class RagDocument:
    """Structured RAG representation of one video analysis."""

    job_id: str
    mlflow_run_id: str | None
    title: str
    content: str
    content_sha256: str
    metadata: dict[str, Any]
    chunks: list[RagChunk]


def _format_mapping(
    value: dict[str, Any] | None,
) -> str:
    if not value:
        return "none"

    return ", ".join(
        f"{key}={item}"
        for key, item in sorted(
            value.items()
        )
    )


def _section(
    title: str,
    lines: list[str],
) -> str:
    return "\n".join(
        [
            f"## {title}",
            *lines,
        ]
    )


def build_analysis_document(
    summary: dict[str, Any],
    *,
    job_id: str,
    mlflow_run_id: str | None = None,
) -> RagDocument:
    """Convert an analysis summary into semantic RAG chunks."""

    model_name = str(
        summary.get(
            "model_name",
            "unknown",
        )
    )

    detection_counts = summary.get(
        "detections_by_label",
        {},
    )

    unique_tracks = summary.get(
        "unique_tracks_by_label",
        {},
    )

    team_counts = summary.get(
        "team_counts",
        {},
    )

    team_assignments = summary.get(
        "team_assignments",
        {},
    )

    metadata_section = _section(
        "Analysis metadata",
        [
            f"Job ID: {job_id}",
            (
                "MLflow run ID: "
                f"{mlflow_run_id or 'unknown'}"
            ),
            f"Model: {model_name}",
            (
                "Input video: "
                f"{summary.get('input_path', 'unknown')}"
            ),
            (
                "Output video: "
                f"{summary.get('output_path', 'unknown')}"
            ),
        ],
    )

    processing_section = _section(
        "Video processing",
        [
            (
                "Source FPS: "
                f"{summary.get('source_fps', 0)}"
            ),
            (
                "Effective FPS: "
                f"{summary.get('effective_fps', 0)}"
            ),
            (
                "Frames processed: "
                f"{summary.get('frames_processed', 0)}"
            ),
            (
                "Video duration seconds: "
                f"{summary.get('duration_seconds', 0)}"
            ),
            (
                "Inference seconds: "
                f"{summary.get('inference_seconds', 0)}"
            ),
            (
                "Total processing seconds: "
                f"{summary.get('total_seconds', 0)}"
            ),
        ],
    )

    detection_section = _section(
        "Object detection",
        [
            (
                "Detections by label: "
                f"{_format_mapping(detection_counts)}"
            ),
        ],
    )

    tracking_section = _section(
        "Multi-object tracking",
        [
            (
                "Unique tracks by label: "
                f"{_format_mapping(unique_tracks)}"
            ),
        ],
    )

    team_section = _section(
        "Team classification",
        [
            (
                "Team counts: "
                f"{_format_mapping(team_counts)}"
            ),
            (
                "Classified player tracks: "
                f"{len(team_assignments)}"
            ),
            (
                "Tracks with usable jersey features: "
                f"{summary.get('team_feature_tracks', 0)}"
            ),
            (
                "Team classification coverage: "
                + str(
                    summary.get(
                        "team_classification_coverage",
                        0.0,
                    )
                )
            ),
            (
                "Team silhouette score: "
                + str(
                    summary.get(
                        "team_silhouette_score",
                        "unavailable",
                    )
                )
            ),
        ],
    )

    sections = [
        metadata_section,
        processing_section,
        detection_section,
        tracking_section,
        team_section,
    ]

    chunks = [
        RagChunk(
            index=index,
            content=content,
            metadata={
                "section": section_name,
                "job_id": job_id,
            },
        )
        for index, (
            section_name,
            content,
        ) in enumerate(
            [
                (
                    "analysis_metadata",
                    metadata_section,
                ),
                (
                    "video_processing",
                    processing_section,
                ),
                (
                    "object_detection",
                    detection_section,
                ),
                (
                    "tracking",
                    tracking_section,
                ),
                (
                    "team_classification",
                    team_section,
                ),
            ]
        )
    ]

    content = "\n\n".join(
        sections
    )

    digest = hashlib.sha256(
        content.encode("utf-8")
    ).hexdigest()

    metadata = {
        "job_id": job_id,
        "mlflow_run_id": mlflow_run_id,
        "model_name": model_name,
        "detections_by_label": detection_counts,
        "unique_tracks_by_label": unique_tracks,
        "team_counts": team_counts,
    }

    return RagDocument(
        job_id=job_id,
        mlflow_run_id=mlflow_run_id,
        title=(
            "FootballMatch analysis "
            f"{job_id}"
        ),
        content=content,
        content_sha256=digest,
        metadata=metadata,
        chunks=chunks,
    )


def document_to_dict(
    document: RagDocument,
) -> dict[str, Any]:
    """Convert a RAG document to JSON-serializable data."""

    return {
        "job_id": document.job_id,
        "mlflow_run_id": (
            document.mlflow_run_id
        ),
        "title": document.title,
        "content": document.content,
        "content_sha256": (
            document.content_sha256
        ),
        "metadata": document.metadata,
        "chunks": [
            {
                "index": chunk.index,
                "content": chunk.content,
                "metadata": chunk.metadata,
            }
            for chunk in document.chunks
        ],
    }


def document_to_json(
    document: RagDocument,
) -> str:
    """Serialize a RAG document as formatted JSON."""

    return json.dumps(
        document_to_dict(document),
        indent=2,
        sort_keys=True,
    )
