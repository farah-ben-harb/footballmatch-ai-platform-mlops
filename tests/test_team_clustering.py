import pytest

from footballmatch_api.ml.team_clustering import TeamColorClusterer


def test_team_color_clusterer_groups_two_distinct_colour_populations() -> None:
    clusterer = TeamColorClusterer(random_state=7)

    result = clusterer.fit_predict(
        [[220, 30, 30], [210, 35, 40], [25, 35, 220], [35, 45, 210]]
    )

    assert len(result.labels) == 4
    assert len(set(result.labels)) == 2
    assert len(result.cluster_centers) == 2
    assert result.inertia >= 0


@pytest.mark.parametrize("features", [[], [[1, 2, 3]]])
def test_team_color_clusterer_requires_enough_examples(features: list[list[float]]) -> None:
    with pytest.raises(ValueError, match="Feature count"):
        TeamColorClusterer().fit_predict(features)
