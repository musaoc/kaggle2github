"""
Unit tests for packager.py (repository scaffolding and file generation).
"""

import json
from pathlib import Path
from kaggle2github.packager import RepoPackager

def test_build_repository(tmp_path: Path):
    kernel_dir = tmp_path / "sample-kernel"
    kernel_dir.mkdir()

    # Create dummy notebook
    nb_content = {
        "cells": [
            {
                "cell_type": "code",
                "source": ["import pandas as pd\n", "print('Hello world')\n"],
            }
        ],
        "metadata": {},
        "nbformat": 4,
        "nbformat_minor": 2,
    }
    with open(kernel_dir / "sample-kernel.ipynb", "w", encoding="utf-8") as f:
        json.dump(nb_content, f)

    meta_content = {
        "slug": "sample-kernel",
        "title": "Sample Kernel Project",
    }
    with open(kernel_dir / "kernel-metadata.json", "w", encoding="utf-8") as f:
        json.dump(meta_content, f)

    output_dir = tmp_path / "repos"
    packager = RepoPackager(
        author="Tester",
        kaggle_user="testkaggle",
        github_user="testgh",
    )

    result = packager.build_repository(
        kernel_dir=kernel_dir,
        output_dir=output_dir,
        repo_name="sample-kernel-repo",
    )

    repo_dir = output_dir / "sample-kernel-repo"
    assert repo_dir.exists()
    assert (repo_dir / "notebooks" / "sample-kernel-repo.ipynb").exists()
    assert (repo_dir / "src" / "main.py").exists()
    assert (repo_dir / "requirements.txt").exists()
    assert (repo_dir / ".gitignore").exists()
    assert (repo_dir / "LICENSE").exists()
    assert (repo_dir / "README.md").exists()

    # Check requirements
    reqs = (repo_dir / "requirements.txt").read_text()
    assert "pandas" in reqs

    # Check src/main.py has resolver and code
    main_py = (repo_dir / "src" / "main.py").read_text()
    assert "_resolve_data_path" in main_py
    assert "print('Hello world')" in main_py

    # Check README has title and author
    readme = (repo_dir / "README.md").read_text()
    assert "Sample Kernel Project" in readme
    assert "Tester" in readme
