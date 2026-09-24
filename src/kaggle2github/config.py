"""
Configuration and credentials management for kaggle2github.
"""

import os
import json
from pathlib import Path
from typing import Optional, Tuple

DEFAULT_DOWNLOAD_DIR = "downloaded_kernels"
DEFAULT_REPOS_DIR = "repos"

def get_kaggle_credentials() -> Tuple[Optional[str], Optional[str]]:
    """
    Retrieve Kaggle credentials from environment variables or ~/.kaggle/kaggle.json.
    Returns (username, key).
    """
    username = os.environ.get("KAGGLE_USERNAME")
    key = os.environ.get("KAGGLE_KEY")
    if username and key:
        return username, key

    # Check ~/.kaggle/kaggle.json
    kaggle_json = Path.home() / ".kaggle" / "kaggle.json"
    if kaggle_json.exists():
        try:
            with open(kaggle_json, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("username"), data.get("key")
        except Exception:
            pass

    return None, None

def get_github_token() -> Optional[str]:
    """
    Retrieve GitHub Personal Access Token from environment variables.
    Checks GITHUB_TOKEN and GH_TOKEN.
    """
    return os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")

def find_downloaded_kaggle_json() -> Optional[Path]:
    """
    Look for a recently downloaded kaggle.json in the user's Downloads directory.
    """
    candidates = [
        Path.home() / "Downloads" / "kaggle.json",
        Path.home() / "downloads" / "kaggle.json",
        Path.cwd() / "kaggle.json",
    ]
    for c in candidates:
        if c.is_file():
            try:
                with open(c, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if data.get("username") and data.get("key"):
                        return c
            except Exception:
                continue
    return None

def install_kaggle_json(source_path: Path) -> Path:
    """
    Copy a kaggle.json file to ~/.kaggle/kaggle.json, creating directory if needed.
    """
    kaggle_dir = Path.home() / ".kaggle"
    kaggle_dir.mkdir(parents=True, exist_ok=True)
    target = kaggle_dir / "kaggle.json"
    
    with open(source_path, "r", encoding="utf-8") as src:
        content = src.read()
    with open(target, "w", encoding="utf-8") as dst:
        dst.write(content)
        
    if os.name != "nt":
        try:
            os.chmod(target, 0o600)
        except Exception:
            pass
            
    # Also update environment for current process
    try:
        data = json.loads(content)
        if data.get("username"):
            os.environ["KAGGLE_USERNAME"] = data["username"]
        if data.get("key"):
            os.environ["KAGGLE_KEY"] = data["key"]
    except Exception:
        pass
        
    return target

def save_kaggle_credentials(username: str, key: str) -> Path:
    """
    Write username and key to ~/.kaggle/kaggle.json, creating directory if needed.
    """
    kaggle_dir = Path.home() / ".kaggle"
    kaggle_dir.mkdir(parents=True, exist_ok=True)
    target = kaggle_dir / "kaggle.json"
    
    data = {"username": username.strip(), "key": key.strip()}
    with open(target, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        
    if os.name != "nt":
        try:
            os.chmod(target, 0o600)
        except Exception:
            pass
            
    os.environ["KAGGLE_USERNAME"] = data["username"]
    os.environ["KAGGLE_KEY"] = data["key"]
    return target

