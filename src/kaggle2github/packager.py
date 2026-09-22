"""
Multi-repository generator for scaffolding standalone GitHub projects from Kaggle notebooks.
"""

import datetime
import glob
import json
import os
import shutil
from pathlib import Path
from typing import Dict, Optional

from kaggle2github.analyzer import analyze_notebook
from kaggle2github.templates import (
    DATA_PATH_RESOLVER_CODE,
    GITIGNORE_TEMPLATE,
    MIT_LICENSE_TEMPLATE,
    generate_readme,
)

class RepoPackager:
    """Builds a production-ready, standalone repository from a downloaded notebook."""

    def __init__(
        self,
        author: str = "Author",
        kaggle_user: str = "kaggle-user",
        github_user: str = "github-user",
        default_year: Optional[int] = None,
    ):
        self.author = author
        self.kaggle_user = kaggle_user
        self.github_user = github_user
        self.year = default_year or datetime.datetime.now().year

    def build_repository(
        self,
        kernel_dir: Path,
        output_dir: Path,
        repo_name: Optional[str] = None,
        custom_metadata: Optional[Dict] = None,
    ) -> Dict:
        """
        Builds a standalone project repository from a kernel directory.
        """
        kernel_dir = Path(kernel_dir)
        output_dir = Path(output_dir)

        # 1. Find .ipynb file
        nb_files = list(kernel_dir.glob("*.ipynb"))
        if not nb_files:
            raise FileNotFoundError(f"No .ipynb file found in {kernel_dir}")
        nb_path = nb_files[0]

        # 2. Extract metadata
        meta_file = kernel_dir / "kernel-metadata.json"
        meta = {}
        if meta_file.exists():
            try:
                with open(meta_file, "r", encoding="utf-8") as f:
                    meta = json.load(f)
            except Exception:
                pass

        slug = meta.get("slug") or kernel_dir.name
        title = meta.get("title") or slug.replace("-", " ").replace("_", " ").title()
        repo_name = repo_name or slug.replace("_", "-").lower()

        # Check custom metadata overrides if provided
        custom_metadata = custom_metadata or {}
        repo_name = custom_metadata.get("repo_name", repo_name)
        title = custom_metadata.get("title", title)
        first_line = custom_metadata.get(
            "first_line",
            f"An end-to-end machine learning project focusing on {title} with leak-free preprocessing and structured modeling."
        )
        category = custom_metadata.get("category", "Machine Learning")
        highlights = custom_metadata.get("highlights", [])
        diagram = custom_metadata.get("diagram", "")

        # Dataset details
        comp_sources = meta.get("competition_sources", [])
        dataset_sources = meta.get("dataset_sources", [])
        competition = comp_sources[0] if comp_sources else custom_metadata.get("competition")
        dataset = dataset_sources[0] if dataset_sources else custom_metadata.get("dataset")

        if competition:
            dataset_name = competition
            dataset_url = f"https://www.kaggle.com/c/{competition}"
            download_cmd = f"kaggle competitions download -c {competition}"
        elif dataset:
            dataset_name = dataset
            dataset_url = f"https://www.kaggle.com/datasets/{dataset}"
            download_cmd = f"kaggle datasets download -d {dataset}"
        else:
            dataset_name = "Kaggle Dataset"
            dataset_url = f"https://www.kaggle.com/code/{self.kaggle_user}/{slug}"
            download_cmd = f"kaggle kernels pull {self.kaggle_user}/{slug} -m"

        kaggle_url = f"https://www.kaggle.com/code/{self.kaggle_user}/{slug}"

        # 3. Analyze notebook and extract clean code & dependencies
        analysis = analyze_notebook(str(nb_path))
        clean_code = analysis["clean_code"]
        dependencies = custom_metadata.get("dependencies") or analysis["dependencies"]

        # Ensure basic essentials if none detected
        if not dependencies:
            dependencies = ["pandas", "numpy", "scikit-learn"]

        # 4. Target repository directory
        repo_dir = output_dir / repo_name
        notebooks_dir = repo_dir / "notebooks"
        src_dir = repo_dir / "src"

        notebooks_dir.mkdir(parents=True, exist_ok=True)
        src_dir.mkdir(parents=True, exist_ok=True)

        # 5. Copy original notebook
        dest_nb = notebooks_dir / f"{repo_name}.ipynb"
        shutil.copy2(nb_path, dest_nb)

        # 6. Generate src/main.py
        main_py_content = f'''"""
{title}
{first_line}

Original Kaggle Notebook: {kaggle_url}
Author: {self.author}
"""

import os
import sys
import warnings
warnings.filterwarnings("ignore")

{DATA_PATH_RESOLVER_CODE}

# --- Pipeline Execution ---
{clean_code}

if __name__ == "__main__":
    print("Pipeline execution completed successfully.")
'''
        with open(src_dir / "main.py", "w", encoding="utf-8") as f:
            f.write(main_py_content)

        # 7. Write requirements.txt
        with open(repo_dir / "requirements.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(dependencies) + "\n")

        # 8. Write .gitignore
        with open(repo_dir / ".gitignore", "w", encoding="utf-8") as f:
            f.write(GITIGNORE_TEMPLATE)

        # 9. Write LICENSE
        with open(repo_dir / "LICENSE", "w", encoding="utf-8") as f:
            f.write(MIT_LICENSE_TEMPLATE.format(year=self.year, author=self.author))

        # 10. Write README.md
        readme = generate_readme(
            title=title,
            repo_name=repo_name,
            first_line=first_line,
            kaggle_url=kaggle_url,
            category=category,
            highlights=highlights,
            diagram=diagram,
            dataset_name=dataset_name,
            dataset_url=dataset_url,
            download_cmd=download_cmd,
            author=self.author,
            kaggle_user=self.kaggle_user,
            github_user=self.github_user,
        )
        with open(repo_dir / "README.md", "w", encoding="utf-8") as f:
            f.write(readme)

        return {
            "repo_name": repo_name,
            "repo_dir": str(repo_dir),
            "title": title,
            "dependencies": dependencies,
            "total_cells": analysis["total_cells"],
            "code_cells": analysis["code_cells_count"],
        }
