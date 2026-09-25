"""
Unit tests for KaggleClient kernel listing and privacy filtering.
"""

from unittest.mock import MagicMock
from kaggle2github.kaggle_client import KaggleClient

class DummyKernel:
    def __init__(self, slug, is_private=False):
        self.ref = f"testuser/{slug}"
        self.slug = slug
        self.title = f"Title for {slug}"
        self.author = "testuser"
        self.totalVotes = 10
        self.totalViews = 100
        self.lastRunTime = "2026-01-01"
        self.is_private = is_private

def test_list_kernels_filters_private_by_default(monkeypatch):
    client = KaggleClient(username="testuser", key="testkey")

    mock_api = MagicMock()
    mock_api.kernels_list.return_value = [
        DummyKernel("public-eda", is_private=False),
        DummyKernel("secret-experiment", is_private=True),
        DummyKernel("model-benchmark", is_private=False),
    ]
    monkeypatch.setattr(client, "_get_api", lambda: mock_api)

    # Default: public only
    public_kernels = client.list_kernels(user="testuser")
    slugs = [k["slug"] for k in public_kernels]
    assert "public-eda" in slugs
    assert "model-benchmark" in slugs
    assert "secret-experiment" not in slugs
    assert len(public_kernels) == 2

def test_list_kernels_includes_private_when_flag_set(monkeypatch):
    client = KaggleClient(username="testuser", key="testkey")

    mock_api = MagicMock()
    mock_api.kernels_list.return_value = [
        DummyKernel("public-eda", is_private=False),
        DummyKernel("secret-experiment", is_private=True),
    ]
    monkeypatch.setattr(client, "_get_api", lambda: mock_api)

    all_kernels = client.list_kernels(user="testuser", include_private=True)
    slugs = [k["slug"] for k in all_kernels]
    assert "public-eda" in slugs
    assert "secret-experiment" in slugs
    assert len(all_kernels) == 2
