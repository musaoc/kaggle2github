import concurrent.futures
import json
import os
import shutil
from pathlib import Path
from typing import Dict, List, Optional
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

    def is_kernel_private(self, user: str, slug: str) -> bool:
        """
        Check whether a specific kernel is private using the Kaggle SDK.
        """
        try:
            from kagglesdk.kernels.types.kernels_api_service import ApiGetKernelRequest
            api = self._get_api()
            client = api.build_kaggle_client()
            req = ApiGetKernelRequest()
            req.user_name = user
            req.kernel_slug = slug
            resp = client.kernels.kernels_api_client.get_kernel(req)
            if resp and resp.metadata:
                return bool(getattr(resp.metadata, "is_private", False))
        except Exception:
            pass
        return False

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

        kernel_items = []
        for k in raw_kernels:
            ref = getattr(k, "ref", "")
            slug = ref.split("/")[-1] if "/" in ref else getattr(k, "slug", "")
            kernel_items.append({
                "ref": ref,
                "slug": slug,
                "title": getattr(k, "title", slug),
                "author": getattr(k, "author", target_user),
                "votes": getattr(k, "totalVotes", 0) or getattr(k, "total_votes", 0),
                "views": getattr(k, "totalViews", 0) or getattr(k, "total_views", 0),
                "url": f"https://www.kaggle.com/code/{ref}",
                "last_run": str(getattr(k, "lastRunTime", "") or getattr(k, "last_run_time", "")),
            })

        if not include_private and kernel_items:
            # Check privacy in parallel for fast verification
            def _check(item):
                is_priv = self.is_kernel_private(target_user, item["slug"])
                return item, is_priv

            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                checked = list(executor.map(_check, kernel_items))

            results = []
            for item, is_priv in checked:
                if not is_priv:
                    item["is_private"] = False
                    results.append(item)
            return results

        for item in kernel_items:
            item["is_private"] = False
        return kernel_items

    def download_kernel(
        self,
        slug: str,
        output_dir: str,
        user: Optional[str] = None,
        include_private: bool = False,
    ) -> Optional[Path]:
        """
        Download a single kernel into output_dir/<slug>/.
        If include_private is False and kernel is detected as private, it is skipped and removed.
        """
        target_user = user or self.username
        if not target_user:
            raise ValueError("Kaggle username must be specified to download kernels.")

        dest_dir = Path(output_dir) / slug
        dest_dir.mkdir(parents=True, exist_ok=True)

        api = self._get_api()
        kernel_ref = f"{target_user}/{slug}"
        api.kernels_pull(kernel_ref, path=str(dest_dir), metadata=True)

        # Verify against downloaded kernel-metadata.json
        meta_file = dest_dir / "kernel-metadata.json"
        if meta_file.exists():
            try:
                with open(meta_file, "r", encoding="utf-8") as f:
                    meta = json.load(f)
                if not include_private and meta.get("is_private") is True:
                    shutil.rmtree(dest_dir, ignore_errors=True)
                    return None
            except Exception:
                pass

        return dest_dir
