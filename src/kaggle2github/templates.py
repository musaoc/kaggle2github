"""
Templates for repository scaffolding, licenses, .gitignore, and documentation.
"""

from typing import Optional

GITIGNORE_TEMPLATE = """# Python byte-code
__pycache__/
*.py[cod]
*$py.class
*.so

# Environments
venv/
.venv/
env/
ENV/

# Jupyter
.ipynb_checkpoints
*/.ipynb_checkpoints/*

# Model weights & large binaries
*.pt
*.pth
*.h5
*.keras
*.onnx
*.pkl
*.joblib
runs/
wandb/

# Local data files
data/
*.csv
*.tsv
*.xlsx
*.parquet
*.feather
*.zip
*.tar.gz

# IDE & OS
.DS_Store
Thumbs.db
.vscode/
.idea/
.env
.env.*
"""

MIT_LICENSE_TEMPLATE = """MIT License

Copyright (c) {year} {author}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

DATA_PATH_RESOLVER_CODE = """# --- Smart Dataset Path Resolution ---
def _resolve_data_path(file_path: str) -> str:
    \"\"\"Checks local and data/ directories if Kaggle dataset path is missing.\"\"\"
    if os.path.exists(file_path):
        return file_path
    base = os.path.basename(file_path)
    candidates = [
        base,
        os.path.join("data", base),
        os.path.join("..", "data", base),
        file_path.replace("/kaggle/input/", "data/"),
        file_path.replace("../input/", "data/"),
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return file_path
"""

def generate_readme(
    title: str,
    repo_name: str,
    first_line: str,
    kaggle_url: str,
    category: str = "",
    highlights: Optional[list] = None,
    diagram: str = "",
    dataset_name: str = "Kaggle Dataset",
    dataset_url: str = "",
    download_cmd: str = "",
    author: str = "Author",
    kaggle_user: str = "kaggle-user",
    github_user: str = "github-user",
) -> str:
    """
    Generate a clean, reproducible, and lightweight README.md.
    If highlights or diagram are provided (e.g., enriched via AGENTS.md), they are included;
    otherwise, a clean, honest quickstart is generated without fake placeholder diagrams.
    """
    highlights = highlights or []
    category_badge = category.replace(' ', '%20').replace('-', '--') if category else "Machine%20Learning"

    sections = [
        f"# {title}",
        "",
        first_line,
        "",
        f"[![Kaggle Notebook](https://img.shields.io/badge/Kaggle-Notebook-20BEFF?logo=kaggle&logoColor=white)]({kaggle_url})",
        f"[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)",
        "![Python 3.9+](https://img.shields.io/badge/Python-3.9+-blue.svg?logo=python&logoColor=white)",
        f"![Category](https://img.shields.io/badge/Topic-{category_badge}-brightgreen)",
        "",
        "---",
        "",
        "## Overview",
        "",
        f"This repository is a clean, modular export of the Kaggle notebook **[{title}]({kaggle_url})**.",
        "It includes sanitized code, extracted dependencies, and local dataset path handling for immediate local execution.",
    ]

    # Optional AI-enriched highlights if provided
    if highlights:
        sections.extend([
            "",
            "---",
            "",
            "## Key Highlights & Methodology",
            "",
            "\n".join([f"- {h}" for h in highlights]),
        ])

    # Optional system architecture diagram if provided
    if diagram:
        sections.extend([
            "",
            "---",
            "",
            "## System Architecture",
            "",
            diagram,
        ])

    sections.extend([
        "",
        "---",
        "",
        "## Repository Structure",
        "",
        "```plaintext",
        f"{repo_name}/",
        f"├── notebooks/",
        f"│   └── {repo_name}.ipynb      # Original Jupyter notebook with visuals & outputs",
        f"├── src/",
        f"│   └── main.py                # Standalone, runnable pipeline script",
        f"├── .gitignore                 # Standard Python, Jupyter, model weight & data ignores",
        f"├── LICENSE                    # MIT License",
        f"├── requirements.txt           # Minimal verified dependencies",
        f"└── README.md                  # Project documentation",
        "```",
        "",
        "---",
        "",
        "## Quickstart & Reproduction",
        "",
        "### 1. Clone the Repository",
        "```bash",
        f"git clone https://github.com/{github_user}/{repo_name}.git",
        f"cd {repo_name}",
        "```",
        "",
        "### 2. Set Up Virtual Environment",
        "```bash",
        "# Linux / macOS",
        "python3 -m venv venv",
        "source venv/bin/activate",
        "",
        "# Windows PowerShell",
        "python -m venv venv",
        ".\\venv\\Scripts\\Activate.ps1",
        "```",
        "",
        "### 3. Install Dependencies",
        "```bash",
        "pip install --upgrade pip",
        "pip install -r requirements.txt",
        "```",
        "",
        "### 4. Run the Pipeline",
        "Execute the clean standalone script:",
        "```bash",
        "python src/main.py",
        "```",
        "",
        "Or launch and explore the original interactive notebook:",
        "```bash",
        f"jupyter lab notebooks/{repo_name}.ipynb",
        "```",
    ])

    if dataset_name and (dataset_url or download_cmd):
        sections.extend([
            "",
            "---",
            "",
            "## Dataset Details",
            "",
            f"- **Source**: [{dataset_name}]({dataset_url})" if dataset_url else f"- **Source**: {dataset_name}",
            f"- **Download Command**:\n  ```bash\n  {download_cmd}\n  ```" if download_cmd else "",
            "",
            "Place downloaded dataset files inside a `data/` folder in the project root. The `src/main.py` script automatically detects paths.",
        ])

    sections.extend([
        "",
        "---",
        "",
        "## 🤖 AI Enrichment & Deep Architecture",
        "",
        "This project was migrated using [kaggle2github](https://github.com/musaoc/kaggle2github).",
        "",
        "> [!TIP]",
        "> To generate custom architecture flowcharts (Mermaid), deep code audits, and recruiter-grade project highlights for this project, run an AI coding agent (e.g. Antigravity, Cursor, Claude Code) following the [**`AGENTS.md`**](https://github.com/musaoc/kaggle2github/blob/main/AGENTS.md) protocol.",
        "",
        "---",
        "",
        "## Author & Acknowledgments",
        "",
        f"- **Author**: {author}",
        f"- **Kaggle**: [@{kaggle_user}](https://www.kaggle.com/{kaggle_user})",
        f"- **GitHub**: [@{github_user}](https://github.com/{github_user})",
        f"- **Original Kaggle Notebook**: [{title}]({kaggle_url})",
        "",
    ])

    return "\n".join(sections)

