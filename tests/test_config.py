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

def test_save_and_load_env_credentials(tmp_path: Path, monkeypatch):
    env_file = tmp_path / ".env"
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("KAGGLE_USERNAME", raising=False)
    monkeypatch.delenv("KAGGLE_KEY", raising=False)
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)

    from kaggle2github.config import save_env_credentials, load_env, get_kaggle_credentials, get_github_token

    saved = save_env_credentials(
        kaggle_username="env_user",
        kaggle_key="env_key789",
        github_token="ghp_envtoken123",
        env_path=env_file,
    )
    assert saved.exists()
    content = saved.read_text(encoding="utf-8")
    assert "KAGGLE_USERNAME=env_user" in content
    assert "KAGGLE_KEY=env_key789" in content
    assert "GITHUB_TOKEN=ghp_envtoken123" in content

    # Clear env vars and reload from file
    monkeypatch.delenv("KAGGLE_USERNAME", raising=False)
    monkeypatch.delenv("KAGGLE_KEY", raising=False)
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)

    assert load_env(env_file) is True
    u, k = get_kaggle_credentials()
    gh = get_github_token()
    assert u == "env_user"
    assert k == "env_key789"
    assert gh == "ghp_envtoken123"
