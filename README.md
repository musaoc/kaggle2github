# kaggle2github 🚀

> **Effortlessly shift your public Kaggle work into standalone, recruiter-ready GitHub repositories in minutes.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9+-blue.svg?logo=python&logoColor=white)](https://www.python.org/downloads/)
[![Kaggle API](https://img.shields.io/badge/Kaggle-API%20Integrated-20BEFF?logo=kaggle&logoColor=white)](https://github.com/Kaggle/kaggle-api)
[![GitHub API](https://img.shields.io/badge/GitHub-REST%20API-181717?logo=github&logoColor=white)](https://docs.github.com/en/rest)

---

## Why `kaggle2github`?

Data scientists and ML engineers build impressive notebooks on Kaggle, but **recruiters, engineering teams, and hiring managers look at GitHub profiles**. 

Kaggle notebooks often fail when pushed directly to GitHub:
- Hardcoded `/kaggle/input/...` paths crash when run on local machines.
- IPython shell magics (`!pip install`, `%matplotlib inline`, `%cd`) break standard Python execution.
- Missing `requirements.txt`, licenses, modular entrypoints, and `.gitignore`.

`kaggle2github` automatically transforms your public Kaggle notebooks into independent, executable, and clean GitHub repositories published directly to your public GitHub profile.

---

## ⚡ 3-Minute Quickstart

### 1. Install
```bash
# Clone and install in editable mode
git clone https://github.com/musaoc/kaggle2github.git
cd kaggle2github
pip install -e .
```

### 2. Connect Your Accounts
Run the interactive setup helper:
```bash
kaggle2github setup
```
*(Verifies credentials, detects downloaded `kaggle.json`, and can save directly to a `.env` file).*

### 3. Run Full Migration
Migrate all your **public** Kaggle notebooks into clean, public GitHub repositories in one command:
```bash
kaggle2github run-all --user <your_kaggle_username> --github-user <your_github_username>
```

> 🌐 **Public by Default**: By default, only your **public** Kaggle work is downloaded and published as **public** GitHub repositories. Private notebooks are never touched unless you explicitly pass `--include-private`.

---

## 🔑 Authentication & Credentials

You can authenticate in any of the following three ways:

### Method 1: Interactive Setup Wizard (Recommended)
```bash
kaggle2github setup
```
- Automatically detects `kaggle.json` in your `Downloads` folder.
- Verifies your GitHub token and Kaggle keys on the spot.
- **To switch accounts or change tokens:** Run `kaggle2github setup --reconfigure`.

### Method 2: Local `.env` File
Copy [.env.example](.env.example) to `.env` in the repository root:
```bash
# On Linux/macOS
cp .env.example .env

# On Windows PowerShell
Copy-Item .env.example .env
```
Fill in your credentials:
```ini
KAGGLE_USERNAME=your_kaggle_username
KAGGLE_KEY=your_kaggle_api_key
GITHUB_TOKEN=ghp_your_github_token
```
`kaggle2github` automatically loads this `.env` file for every command.

### Method 3: System Environment / Files
- **Kaggle**: Place `kaggle.json` in `~/.kaggle/kaggle.json` (or set `KAGGLE_USERNAME` and `KAGGLE_KEY`).
- **GitHub**: Set `GITHUB_TOKEN="ghp_xxx"` in your terminal (`$env:GITHUB_TOKEN` on PowerShell / `export GITHUB_TOKEN` on Linux/macOS).

---

## 🛠️ Step-by-Step CLI Usage

If you prefer executing the pipeline step-by-step:

### 1. Scan your Kaggle Notebooks
Explore your public work, vote counts, and view metrics:
```bash
kaggle2github scan --user <your_kaggle_username>
```

### 2. Download Selected or All Notebooks
Download notebooks into a local staging directory (`downloaded_kernels/`):
```bash
# Download all public notebooks
kaggle2github download --user <your_kaggle_username>

# Or download specific notebooks by slug
kaggle2github download --user <your_kaggle_username> --slugs house-prices-eda spaceship-titanic
```

### 3. Build Standalone Repositories
Transform downloaded notebooks into standalone project structures:
```bash
kaggle2github build --input-dir downloaded_kernels --output-dir repos
```

### 4. Publish to GitHub
Push repositories to your GitHub account (**Public** by default):
```bash
# Publish publicly (default)
kaggle2github publish --repos-dir repos --user <your_github_username>

# Or publish as private repositories
kaggle2github publish --repos-dir repos --user <your_github_username> --private
```

---

## 📦 What Each Generated Repository Contains

Each generated repository is clean, self-contained, and runnable:

```plaintext
my-project-repo/
├── notebooks/
│   └── my-project-repo.ipynb    # Original Jupyter notebook with visuals & outputs
├── src/
│   └── main.py                  # Standalone, runnable script with smart /kaggle/input/ fallback
├── .gitignore                   # Ignores byte-code, virtual environments, data, and model weights
├── LICENSE                      # MIT License
├── requirements.txt             # Auto-extracted minimal dependencies
└── README.md                    # Clean, lightweight project documentation & reproduction steps
```

---

## 🤖 AI Deep Enrichment via `AGENTS.md` (Optional)

`kaggle2github` intentionally keeps the default CLI output clean, honest, and lightweight without fake boilerplate diagrams.

If you want **deep architectural flowcharts (Mermaid)**, in-depth technical highlights, domain-specific problem formulations, and metric benchmarks:

1. Open your AI coding agent (e.g. **Antigravity**, **Cursor**, **Claude Code**, or **Copilot**).
2. Point the agent to **[`AGENTS.md`](AGENTS.md)**.
3. The agent will read your notebook cells, analyze your data transformations, and generate custom architecture diagrams and recruiter-grade case studies!

---

## Contributing & License

Contributions, feedback, and pull requests are warmly welcomed!
Licensed under the [MIT License](LICENSE).
