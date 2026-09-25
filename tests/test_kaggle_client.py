"""
Unit tests for KaggleClient kernel listing and privacy filtering.
"""

import json
from pathlib import Path
from unittest.mock import MagicMock
from kaggle2github.kaggle_client import KaggleClient

class DummyKernel:
    def __init__(self, slug):
        self.ref = f"testuser/{slug}"
        self.slug = slug
        self.title = f"Title for {slug}"
        self.author = "testuser"
        self.totalVotes = 10
        self.totalViews = 100
        self.lastRunTime = "2026-01-01"

def test_list_kernels_filters_private_by_default(monkeypatch):
    client = KaggleClient(username="testuser", key="testkey")

    mock_api = MagicMock()
    mock_api.kernels_list.return_value = [
        DummyKernel("public-eda"),
        DummyKernel("secret-experiment"),
        DummyKernel("model-benchmark"),
    ]
    monkeypatch.setattr(client, "_get_api", lambda: mock_api)
    monkeypatch.setattr(client, "is_kernel_private", lambda u, s: s == "secret-experiment")

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
        DummyKernel("public-eda"),
        DummyKernel("secret-experiment"),
    ]
    monkeypatch.setattr(client, "_get_api", lambda: mock_api)
    monkeypatch.setattr(client, "is_kernel_private", lambda u, s: s == "secret-experiment")

    all_kernels = client.list_kernels(user="testuser", include_private=True)
    slugs = [k["slug"] for k in all_kernels]
    assert "public-eda" in slugs
    assert "secret-experiment" in slugs
    assert len(all_kernels) == 2

def test_download_kernel_skips_and_cleans_private(tmp_path: Path, monkeypatch):
    client = KaggleClient(username="testuser", key="testkey")

    def mock_pull(ref, path, metadata):
        dest = Path(path)
        dest.mkdir(parents=True, exist_ok=True)
        (dest / "notebook.ipynb").write_text("{}", encoding="utf-8")
        (dest / "kernel-metadata.json").write_text(json.dumps({"is_private": True}), encoding="utf-8")

    mock_api = MagicMock()
    mock_api.kernels_pull = mock_pull
    monkeypatch.setattr(client, "_get_api", lambda: mock_api)

    # When include_private=False, private kernel should be removed and return None
    res = client.download_kernel("secret-slug", output_dir=str(tmp_path), user="testuser", include_private=False)
    assert res is None
    assert not (tmp_path / "secret-slug").exists()
