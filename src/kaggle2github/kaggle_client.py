"""
Kaggle API client wrapper for listing and downloading user kernels.
"""

import os
from typing import Dict, List, Optional
from pathlib import Path
from kaggle2github.config import get_kaggle_credentials

class KaggleClient:
    """Wrapper around Kaggle API for kernel discovery and downloads."""

    def __init__(self, username: Optional[str] = None, key: Optional[str] = None):
        cred_user, cred_key = get_kaggle_credentials()
        self.username = username or cred_user
        self.key = key or cred_key

        if self.username and self.key:
            os.environ["KAGGLE_USERNAME"] = self.username
            os.environ["KAGGLE_KEY"] = self.key

        self._api = None

    def _get_api(self):
        if self._api is None:
            try:
                from kaggle.api.kaggle_api_extended import KaggleApi
                api = KaggleApi()
                api.authenticate()
                self._api = api
            except Exception as e:
                raise RuntimeError(
                    f"Failed to authenticate with Kaggle API: {e}\n"
                    "Please ensure ~/.kaggle/kaggle.json exists or KAGGLE_USERNAME/KAGGLE_KEY are set."
                )
        return self._api

    def list_kernels(
        self,
        user: Optional[str] = None,
        page_size: int = 100,
        include_private: bool = False,
    ) -> List[Dict]:
        """
        List kernels for the given user. By default, lists ONLY public kernels.
        """
        target_user = user or self.username
        if not target_user:
            raise ValueError("Kaggle username must be specified to list kernels.")

        api = self._get_api()
        raw_kernels = api.kernels_list(user=target_user, page_size=page_size) or []

        results = []
        for k in raw_kernels:
            is_priv = bool(getattr(k, "is_private", False) or getattr(k, "isPrivate", False))
            if not include_private and is_priv:
                continue

            ref = getattr(k, "ref", "")
            slug = ref.split("/")[-1] if "/" in ref else getattr(k, "slug", "")
            results.append({
                "ref": ref,
                "slug": slug,
                "title": getattr(k, "title", slug),
                "author": getattr(k, "author", target_user),
                "votes": getattr(k, "totalVotes", 0) or getattr(k, "total_votes", 0),
                "views": getattr(k, "totalViews", 0) or getattr(k, "total_views", 0),
                "url": f"https://www.kaggle.com/code/{ref}",
                "last_run": str(getattr(k, "lastRunTime", "") or getattr(k, "last_run_time", "")),
                "is_private": is_priv,
            })

        return results

    def download_kernel(self, slug: str, output_dir: str, user: Optional[str] = None) -> Path:
        """
        Download a single kernel into output_dir/<slug>/.
        """
        target_user = user or self.username
        if not target_user:
            raise ValueError("Kaggle username must be specified to download kernels.")

        dest_dir = Path(output_dir) / slug
        dest_dir.mkdir(parents=True, exist_ok=True)

        api = self._get_api()
        kernel_ref = f"{target_user}/{slug}"
        api.kernels_pull(kernel_ref, path=str(dest_dir), metadata=True)
        return dest_dir
