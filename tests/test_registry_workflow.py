from types import SimpleNamespace

import pytest

from scripts import promote_detector_model


def test_promotion_rejects_candidate_without_smoke_test(monkeypatch):
    promoted = []

    class FakeClient:
        def get_model_version_by_alias(self, *_args):
            return SimpleNamespace(version="2", tags={})

        def set_model_version_tag(self, **_kwargs):
            promoted.append("tag")

        def set_registered_model_alias(self, **_kwargs):
            promoted.append("alias")

    monkeypatch.setattr(promote_detector_model, "MlflowClient", FakeClient)
    monkeypatch.setattr(promote_detector_model.mlflow, "set_tracking_uri", lambda _uri: None)

    with pytest.raises(RuntimeError, match="smoke test"):
        promote_detector_model.main()

    assert promoted == []
