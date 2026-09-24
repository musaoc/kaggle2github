"""
Unit tests for credentials management and config helpers.
"""

import json
from pathlib import Path
from kaggle2github.config import (
    find_downloaded_kaggle_json,
    install_kaggle_json,
    save_kaggle_credentials,
    get_kaggle_credentials,
)

def test_save_kaggle_credentials(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    monkeypatch.delenv("KAGGLE_USERNAME", raising=False)
    monkeypatch.delenv("KAGGLE_KEY", raising=False)

    saved_path = save_kaggle_credentials("test_user", "test_key123")
    assert saved_path.exists()

    with open(saved_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["username"] == "test_user"
    assert data["key"] == "test_key123"

def test_install_kaggle_json(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    
    src = tmp_path / "Downloads" / "kaggle.json"
    src.parent.mkdir(parents=True, exist_ok=True)
    src.write_text(json.dumps({"username": "dl_user", "key": "dl_key456"}), encoding="utf-8")

    installed = install_kaggle_json(src)
    assert installed.exists()
    assert (tmp_path / ".kaggle" / "kaggle.json").exists()

    u, k = get_kaggle_credentials()
    assert u == "dl_user"
    assert k == "dl_key456"
