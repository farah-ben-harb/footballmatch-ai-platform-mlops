"""Jersey-color feature extraction, team clustering, and evaluation."""

from collections import Counter
from typing import Any

import cv2
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

from footballmatch_api.cv.detector import Detection


def extract_jersey_feature(
    frame: Any,
    detection: Detection,
) -> np.ndarray | None:
    """Extract a robust LAB color feature from a player's jersey region."""

    if detection.label != "person":
        return None

    if not hasattr(frame, "shape"):
        return None

    height, width = frame.shape[:2]

    left, top, right, bottom = (
        round(value)
        for value in detection.bounding_box
    )

    left = max(0, min(left, width - 1))
    right = max(0, min(right, width))
    top = max(0, min(top, height - 1))
    bottom = max(0, min(bottom, height))

    if right <= left or bottom <= top:
        return None

    box_width = right - left
    box_height = bottom - top

    jersey_left = left + round(
        box_width * 0.20
    )

    jersey_right = right - round(
        box_width * 0.20
    )

    jersey_top = top + round(
        box_height * 0.20
    )

    jersey_bottom = top + round(
        box_height * 0.55
    )

    if (
        jersey_right <= jersey_left
        or jersey_bottom <= jersey_top
    ):
        return None

    crop = frame[
        jersey_top:jersey_bottom,
        jersey_left:jersey_right,
    ]

    if crop.size == 0:
        return None

    lab = cv2.cvtColor(
        crop,
        cv2.COLOR_BGR2LAB,
    )

    pixels = lab.reshape(
        -1,
        3,
    ).astype(float)

    return np.median(
        pixels,
        axis=0,
    )


def aggregate_track_features(
    samples: dict[int, list[np.ndarray]],
    *,
    min_samples: int = 2,
) -> dict[int, np.ndarray]:
    """Aggregate jersey features for tracks with enough observations."""

    if min_samples < 1:
        raise ValueError(
            "min_samples must be at least 1"
        )

    aggregated: dict[int, np.ndarray] = {}

    for track_id, observations in samples.items():
        if len(observations) < min_samples:
            continue

        aggregated[track_id] = np.mean(
            observations,
            axis=0,
        )

    return aggregated


def cluster_tracks_into_teams(
    track_features: dict[int, np.ndarray],
) -> dict[int, int]:
    """Cluster tracked players into two jersey-color teams."""

    if len(track_features) < 2:
        return {}

    track_ids = sorted(
        track_features
    )

    features = np.vstack(
        [
            track_features[track_id]
            for track_id in track_ids
        ]
    )

    model = KMeans(
        n_clusters=2,
        random_state=42,
        n_init=10,
    )

    raw_labels = model.fit_predict(
        features
    )

    # KMeans cluster IDs are arbitrary.
    # Sort centroids to keep Team 0 / Team 1 deterministic.
    ordered_clusters = sorted(
        range(2),
        key=lambda cluster_id: tuple(
            model.cluster_centers_[
                cluster_id
            ]
        ),
    )

    normalized_labels = {
        raw_cluster: normalized_cluster
        for normalized_cluster, raw_cluster
        in enumerate(
            ordered_clusters
        )
    }

    return {
        track_id: normalized_labels[
            int(raw_label)
        ]
        for track_id, raw_label
        in zip(
            track_ids,
            raw_labels,
            strict=True,
        )
    }


def calculate_team_clustering_quality(
    track_features: dict[int, np.ndarray],
    assignments: dict[int, int],
) -> float | None:
    """Calculate a Silhouette Score when the clustering can be evaluated."""

    track_ids = sorted(
        track_id
        for track_id in assignments
        if track_id in track_features
    )

    if len(track_ids) < 3:
        return None

    labels = np.array(
        [
            assignments[track_id]
            for track_id in track_ids
        ]
    )

    unique_labels = set(
        labels.tolist()
    )

    if len(unique_labels) < 2:
        return None

    if len(unique_labels) >= len(
        track_ids
    ):
        return None

    features = np.vstack(
        [
            track_features[track_id]
            for track_id in track_ids
        ]
    )

    return float(
        silhouette_score(
            features,
            labels,
        )
    )


def count_tracks_by_team(
    assignments: dict[int, int],
) -> dict[str, int]:
    """Return classified track counts for each team."""

    counts = Counter(
        assignments.values()
    )

    return {
        f"team_{team_id}": count
        for team_id, count
        in sorted(
            counts.items()
        )
    }
