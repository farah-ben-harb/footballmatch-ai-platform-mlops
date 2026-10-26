from footballmatch_api.rag.document_builder import (
    build_analysis_document,
    document_to_dict,
)


def sample_summary() -> dict:
    return {
        "input_path": "/runtime/input.mp4",
        "output_path": "/runtime/output.mp4",
        "model_name": (
            "models:/"
            "FootballMatchYOLODetector"
            "@champion"
        ),
        "source_fps": 30.0,
        "effective_fps": 8.0,
        "frames_processed": 240,
        "duration_seconds": 30.0,
        "inference_seconds": 12.0,
        "total_seconds": 15.0,
        "detections_by_label": {
            "person": 420,
            "sports ball": 38,
        },
        "unique_tracks_by_label": {
            "person": 18,
            "sports ball": 4,
        },
        "team_assignments": {
            "1": 0,
            "2": 0,
            "3": 1,
            "4": 1,
        },
        "team_counts": {
            "team_0": 2,
            "team_1": 2,
        },
        "team_feature_tracks": 4,
        "team_classification_coverage": 0.22,
        "team_silhouette_score": 0.71,
    }


def test_build_analysis_document() -> None:
    document = build_analysis_document(
        sample_summary(),
        job_id="job-123",
        mlflow_run_id="run-456",
    )

    assert document.job_id == "job-123"

    assert (
        document.mlflow_run_id
        == "run-456"
    )

    assert len(document.chunks) == 5

    assert (
        len(document.content_sha256)
        == 64
    )

    assert (
        "Multi-object tracking"
        in document.content
    )

    assert (
        "person=18"
        in document.content
    )

    assert (
        "Team silhouette score: 0.71"
        in document.content
    )


def test_chunks_have_semantic_sections() -> None:
    document = build_analysis_document(
        sample_summary(),
        job_id="job-123",
    )

    sections = [
        chunk.metadata["section"]
        for chunk in document.chunks
    ]

    assert sections == [
        "analysis_metadata",
        "video_processing",
        "object_detection",
        "tracking",
        "team_classification",
    ]


def test_document_is_json_serializable() -> None:
    document = build_analysis_document(
        sample_summary(),
        job_id="job-123",
    )

    data = document_to_dict(
        document
    )

    assert data["job_id"] == "job-123"

    assert (
        data["metadata"]["team_counts"]
        == {
            "team_0": 2,
            "team_1": 2,
        }
    )
