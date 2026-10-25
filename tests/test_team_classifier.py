import numpy as np
import pytest

from footballmatch_api.cv.team_classifier import (
    aggregate_track_features,
    calculate_team_clustering_quality,
    cluster_tracks_into_teams,
    count_tracks_by_team,
)


def test_aggregate_track_features() -> None:
    samples = {
        7: [
            np.array([10.0, 20.0, 30.0]),
            np.array([12.0, 22.0, 32.0]),
        ],
        8: [
            np.array([200.0, 180.0, 170.0]),
            np.array([202.0, 182.0, 172.0]),
        ],
    }

    aggregated = aggregate_track_features(
        samples
    )

    assert np.allclose(
        aggregated[7],
        np.array(
            [11.0, 21.0, 31.0]
        ),
    )

    assert np.allclose(
        aggregated[8],
        np.array(
            [201.0, 181.0, 171.0]
        ),
    )


def test_aggregate_filters_tracks_with_too_few_samples() -> None:
    samples = {
        7: [
            np.array([10.0, 20.0, 30.0]),
        ],
        8: [
            np.array([200.0, 180.0, 170.0]),
            np.array([202.0, 182.0, 172.0]),
        ],
    }

    aggregated = aggregate_track_features(
        samples,
        min_samples=2,
    )

    assert 7 not in aggregated
    assert 8 in aggregated


def test_aggregate_rejects_invalid_min_samples() -> None:
    with pytest.raises(
        ValueError,
        match="at least 1",
    ):
        aggregate_track_features(
            {},
            min_samples=0,
        )


def test_cluster_tracks_into_two_teams() -> None:
    features = {
        1: np.array([20.0, 30.0, 40.0]),
        2: np.array([22.0, 31.0, 39.0]),
        3: np.array([210.0, 180.0, 170.0]),
        4: np.array([208.0, 182.0, 172.0]),
    }

    assignments = cluster_tracks_into_teams(
        features
    )

    assert assignments[1] == assignments[2]
    assert assignments[3] == assignments[4]
    assert assignments[1] != assignments[3]


def test_team_clustering_quality_is_high_for_separated_groups() -> None:
    features = {
        1: np.array([20.0, 30.0, 40.0]),
        2: np.array([21.0, 31.0, 39.0]),
        3: np.array([210.0, 180.0, 170.0]),
        4: np.array([211.0, 179.0, 171.0]),
    }

    assignments = cluster_tracks_into_teams(
        features
    )

    score = calculate_team_clustering_quality(
        features,
        assignments,
    )

    assert score is not None
    assert score > 0.9


def test_team_clustering_quality_requires_enough_tracks() -> None:
    features = {
        1: np.array([20.0, 30.0, 40.0]),
        2: np.array([210.0, 180.0, 170.0]),
    }

    assignments = {
        1: 0,
        2: 1,
    }

    assert (
        calculate_team_clustering_quality(
            features,
            assignments,
        )
        is None
    )


def test_count_tracks_by_team() -> None:
    counts = count_tracks_by_team(
        {
            1: 0,
            2: 0,
            3: 1,
            4: 1,
            5: 1,
        }
    )

    assert counts == {
        "team_0": 2,
        "team_1": 3,
    }
