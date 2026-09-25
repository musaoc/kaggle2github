"""
Configuration and credentials management for kaggle2github.
"""

import os
import json
from pathlib import Path
from typing import Optional, Tuple

try:
    from dotenv import load_dotenv, set_key
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False

DEFAULT_DOWNLOAD_DIR = "downloaded_kernels"
DEFAULT_REPOS_DIR = "repos"

def load_env(env_path: Optional[Path] = None) -> bool:
    """
    Load environment variables from a .env file.
    Checks specified path, cwd/.env, or searches upwards.
    """
    if not DOTENV_AVAILABLE:
        return False
    if env_path and Path(env_path).is_file():
        load_dotenv(dotenv_path=env_path, override=True)
        return True

    # Check cwd/.env first
    cwd_env = Path.cwd() / ".env"
    if cwd_env.is_file():
        load_dotenv(dotenv_path=cwd_env, override=False)
        return True

    return bool(load_dotenv(override=False))

# Automatically load .env on module import
load_env()

def get_active_env_file() -> Optional[Path]:
    """Returns the .env path if .env exists in current working directory."""
    cwd_env = Path.cwd() / ".env"
    if cwd_env.is_file():
        return cwd_env
    return None

def get_kaggle_credentials() -> Tuple[Optional[str], Optional[str]]:
    """
    Retrieve Kaggle credentials from environment variables (.env included) or ~/.kaggle/kaggle.json.
    Returns (username, key).
    """
    load_env()
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
    Retrieve GitHub Personal Access Token from environment variables (.env included).
    Checks GITHUB_TOKEN and GH_TOKEN.
    """
    load_env()
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

def save_env_credentials(
    kaggle_username: Optional[str] = None,
    kaggle_key: Optional[str] = None,
    github_token: Optional[str] = None,
    env_path: Optional[Path] = None,
) -> Path:
    """
    Save or update credentials in a .env file.
    Creates the .env file in cwd (or specified path) if it doesn't exist.
    """
    target = env_path or (Path.cwd() / ".env")
    target = Path(target)

    if not target.exists():
        target.touch()

    # Update current process environment
    if kaggle_username:
        os.environ["KAGGLE_USERNAME"] = kaggle_username.strip()
    if kaggle_key:
        os.environ["KAGGLE_KEY"] = kaggle_key.strip()
    if github_token:
        os.environ["GITHUB_TOKEN"] = github_token.strip()

    if DOTENV_AVAILABLE:
        if kaggle_username:
            set_key(str(target), "KAGGLE_USERNAME", kaggle_username.strip(), quote_mode="never")
        if kaggle_key:
            set_key(str(target), "KAGGLE_KEY", kaggle_key.strip(), quote_mode="never")
        if github_token:
            set_key(str(target), "GITHUB_TOKEN", github_token.strip(), quote_mode="never")
    else:
        lines = []
        if target.exists():
            with open(target, "r", encoding="utf-8") as f:
                lines = f.readlines()
        keys_to_set = {}
        if kaggle_username:
            keys_to_set["KAGGLE_USERNAME"] = kaggle_username.strip()
        if kaggle_key:
            keys_to_set["KAGGLE_KEY"] = kaggle_key.strip()
        if github_token:
            keys_to_set["GITHUB_TOKEN"] = github_token.strip()

        new_lines = []
        seen = set()
        for line in lines:
            trimmed = line.strip()
            if "=" in trimmed and not trimmed.startswith("#"):
                k, _ = trimmed.split("=", 1)
                k = k.strip()
                if k in keys_to_set:
                    new_lines.append(f"{k}={keys_to_set[k]}\n")
                    seen.add(k)
                    continue
            new_lines.append(line)
        for k, v in keys_to_set.items():
            if k not in seen:
                new_lines.append(f"{k}={v}\n")
        with open(target, "w", encoding="utf-8") as f:
            f.writelines(new_lines)

    return target

