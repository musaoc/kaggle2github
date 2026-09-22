"""
Templates for repository scaffolding, licenses, .gitignore, and documentation.
"""

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
    category: str,
    highlights: list,
    diagram: str,
    dataset_name: str,
    dataset_url: str,
    download_cmd: str,
    author: str,
    kaggle_user: str,
    github_user: str,
) -> str:
    """Generate professional, recruiter-ready README.md markdown."""
    highlights_md = "\n".join([f"- {h}" for h in highlights]) if highlights else "- Modular data processing and evaluation pipeline.\n- Reproducible experiments with structured parameters."
    
    if not diagram:
        diagram = """```mermaid
flowchart LR
    A[Raw Dataset] --> B[Data Preprocessing & Cleaning]
    B --> C[Feature Engineering]
    C --> D[Model Training & Cross-Validation]
    D --> E[Inference & Metric Evaluation]
```"""

    category_badge = category.replace(' ', '%20').replace('-', '--') if category else "Data%20Science"

    return f"""# {title}

{first_line}

[![Kaggle Notebook](https://img.shields.io/badge/Kaggle-Notebook-20BEFF?logo=kaggle&logoColor=white)]({kaggle_url})
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9+-blue.svg?logo=python&logoColor=white)](https://www.python.org/downloads/)
[![Field](https://img.shields.io/badge/Field-{category_badge}-brightgreen)](#)

---

## Table of Contents
- [Project Overview](#project-overview)
- [Key Highlights & Methodology](#key-highlights--methodology)
- [System Architecture](#system-architecture)
- [Repository Structure](#repository-structure)
- [Quickstart & Reproduction](#quickstart--reproduction)
- [Dataset Details](#dataset-details)
- [Author & Acknowledgments](#author--acknowledgments)

---

## Project Overview

This repository contains the production-structured implementation of **[{title}]({kaggle_url})**, originally published on Kaggle.

The project emphasizes clean, leak-free preprocessing, structured modeling pipelines, and reproducible machine learning workflows.

---

## Key Highlights & Methodology

{highlights_md}

---

## System Architecture

The pipeline follows a structured, modular execution path:

{diagram}

---

## Repository Structure

```plaintext
{repo_name}/
├── notebooks/
│   └── {repo_name}.ipynb      # Original Jupyter notebook with visuals & charts
├── src/
│   └── main.py                # Standalone, runnable Python pipeline
├── .gitignore                 # Comprehensive Python, Jupyter, and data ignores
├── LICENSE                    # MIT License
├── README.md                  # Technical documentation
└── requirements.txt           # Minimal verified dependencies
```

---

## Quickstart & Reproduction

### 1. Clone the Repository
```bash
git clone https://github.com/{github_user}/{repo_name}.git
cd {repo_name}
```

### 2. Set Up a Virtual Environment
```bash
# Linux / macOS
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
.\\venv\\Scripts\\activate
```

### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Run the Pipeline
Execute the complete pipeline script:
```bash
python src/main.py
```

Or explore and run the interactive notebook:
```bash
jupyter lab notebooks/{repo_name}.ipynb
```

---

## Dataset Details

- **Dataset**: [{dataset_name}]({dataset_url})
- **Platform**: Kaggle
- Automated download via Kaggle CLI:
  ```bash
  {download_cmd}
  ```

---

## Author & Acknowledgments

- **Author**: **{author}**
- **Kaggle**: [@{kaggle_user}](https://www.kaggle.com/{kaggle_user})
- **GitHub**: [@{github_user}](https://github.com/{github_user})
- **Original Kaggle Notebook**: [{title}]({kaggle_url})
"""
