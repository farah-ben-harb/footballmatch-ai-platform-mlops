"""Unsupervised jersey-colour clustering for detected players."""

from dataclasses import dataclass

import numpy as np
from sklearn.cluster import KMeans


@dataclass(frozen=True, slots=True)
class TeamClusteringResult:
    """Cluster assignments and centres for jersey-colour features."""

    labels: list[int]
    cluster_centers: list[list[float]]
    inertia: float


class TeamColorClusterer:
    """Group player jersey-colour features into a configured number of teams."""

    def __init__(self, team_count: int = 2, random_state: int = 42) -> None:
        if team_count < 2:
            raise ValueError("Team count must be at least two")
        self.team_count = team_count
        self.random_state = random_state
        self._model: KMeans | None = None

    def fit_predict(self, features: list[list[float]]) -> TeamClusteringResult:
        """Fit K-Means to BGR/RGB-style numerical colour features."""
        if len(features) < self.team_count:
            raise ValueError("Feature count must be at least the requested team count")

        feature_matrix = np.asarray(features, dtype=float)
        if feature_matrix.ndim != 2 or feature_matrix.shape[1] == 0:
            raise ValueError("Features must be a non-empty two-dimensional matrix")

        self._model = KMeans(
            n_clusters=self.team_count,
            random_state=self.random_state,
            n_init="auto",
        )
        labels = self._model.fit_predict(feature_matrix)
        return TeamClusteringResult(
            labels=labels.tolist(),
            cluster_centers=self._model.cluster_centers_.tolist(),
            inertia=float(self._model.inertia_),
        )
