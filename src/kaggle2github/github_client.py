"""
GitHub API client and Git automation for creating repositories and pushing code.
"""

import json
import os
import subprocess
import urllib.error
import urllib.request
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from kaggle2github.config import get_github_token

class GitHubClient:
    """Client for GitHub REST API and Git CLI operations."""

    def __init__(self, token: Optional[str] = None, github_user: Optional[str] = None):
        self.token = token or get_github_token()
        self.github_user = github_user

    def _api_request(self, endpoint: str, method: str = "GET", data: Optional[Dict] = None) -> Optional[Dict]:
        """Perform an authenticated GitHub REST API request using standard library."""
        if not self.token:
            raise ValueError("GitHub token is required for GitHub API operations.")

        url = f"https://api.github.com{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "kaggle2github-tool",
        }
        encoded_data = None
        if data is not None:
            encoded_data = json.dumps(data).encode("utf-8")
            headers["Content-Type"] = "application/json"

        req = urllib.request.Request(url, data=encoded_data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req) as response:
                if response.status in (200, 201):
                    return json.loads(response.read().decode("utf-8"))
                return {"status": response.status}
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            error_body = e.read().decode("utf-8", errors="ignore")
            raise RuntimeError(f"GitHub API Error {e.code} for {url}: {error_body}")

    def get_authenticated_user(self) -> str:
        """Fetch the authenticated GitHub username if not already provided."""
        if self.github_user:
            return self.github_user
        res = self._api_request("/user")
        if res and "login" in res:
            self.github_user = res["login"]
            return self.github_user
        raise RuntimeError("Unable to determine authenticated GitHub user.")

    def ensure_repository(
        self,
        repo_name: str,
        description: str = "",
        private: bool = False,
        topics: Optional[List[str]] = None,
    ) -> Dict:
        """
        Ensures the repository exists on GitHub with the specified visibility and topics.
        """
        user = self.get_authenticated_user()
        repo_info = self._api_request(f"/repos/{user}/{repo_name}")

        if repo_info is None:
            payload = {
                "name": repo_name,
                "description": description,
                "private": private,
                "has_issues": True,
                "has_projects": True,
                "has_wiki": False,
            }
            repo_info = self._api_request("/user/repos", method="POST", data=payload)
        else:
            # Update visibility if necessary
            if repo_info.get("private") != private:
                self._api_request(f"/repos/{user}/{repo_name}", method="PATCH", data={"private": private})

        # Set topics if specified
        if topics:
            clean_topics = [t.lower().replace(" ", "-") for t in topics][:20]
            self._api_request(f"/repos/{user}/{repo_name}/topics", method="PUT", data={"names": clean_topics})

        return repo_info or {}

    def push_repository(
        self,
        repo_path: Path,
        repo_name: str,
        commit_message: str = "feat: initial release with production pipeline, notebook, and documentation",
        user_name: Optional[str] = None,
        user_email: Optional[str] = None,
    ) -> Tuple[bool, str]:
        """
        Initializes Git, commits local files, and pushes to GitHub.
        Cleans the remote URL after push to avoid persisting tokens in git config.
        """
        repo_path = Path(repo_path)
        if not repo_path.exists():
            return False, f"Directory does not exist: {repo_path}"

        user = self.get_authenticated_user()
        git_name = user_name or user
        git_email = user_email or f"{user}@users.noreply.github.com"

        try:
            # 1. Initialize git
            subprocess.run(["git", "init", "-b", "main"], cwd=repo_path, check=True, stdout=subprocess.DEVNULL)
            subprocess.run(["git", "config", "user.name", git_name], cwd=repo_path, check=True)
            subprocess.run(["git", "config", "user.email", git_email], cwd=repo_path, check=True)
            subprocess.run(["git", "add", "."], cwd=repo_path, check=True)

            status = subprocess.run(["git", "status", "--porcelain"], cwd=repo_path, capture_output=True, text=True)
            if status.stdout.strip():
                subprocess.run(["git", "commit", "-m", commit_message], cwd=repo_path, check=True, stdout=subprocess.DEVNULL)

            # 2. Remote configuration with token
            remote_with_token = f"https://x-access-token:{self.token}@github.com/{user}/{repo_name}.git"
            clean_remote = f"https://github.com/{user}/{repo_name}.git"

            remotes = subprocess.run(["git", "remote"], cwd=repo_path, capture_output=True, text=True).stdout
            if "origin" in remotes.split():
                subprocess.run(["git", "remote", "set-url", "origin", remote_with_token], cwd=repo_path, check=True)
            else:
                subprocess.run(["git", "remote", "add", "origin", remote_with_token], cwd=repo_path, check=True)

            # 3. Push to main
            subprocess.run(["git", "push", "-u", "origin", "main", "--force"], cwd=repo_path, check=True, capture_output=True)

            # 4. Clean remote URL to scrub token from local .git/config
            subprocess.run(["git", "remote", "set-url", "origin", clean_remote], cwd=repo_path, check=True)

            return True, f"Successfully pushed {repo_name} to GitHub"
        except subprocess.CalledProcessError as e:
            err = e.stderr.decode("utf-8", errors="ignore") if isinstance(e.stderr, bytes) else str(e)
            return False, f"Git error: {err}"
        except Exception as e:
            return False, str(e)
