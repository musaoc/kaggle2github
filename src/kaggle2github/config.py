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
