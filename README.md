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

### 2. 1-Minute Authentication Wizard
Run the interactive setup helper:
```bash
kaggle2github setup
```
> **What the wizard does for you:**
> - Detects `kaggle.json` if it's already in your `Downloads` folder and installs it automatically.
> - Automatically creates the `~/.kaggle/` directory with secure permissions.
> - Verifies your Kaggle and GitHub credentials on the spot.
> - Offers to save credentials directly to a local `.env` file for easy account switching.
> - **Switch accounts anytime:** Run `kaggle2github setup --reconfigure` or edit your `.env` file!

### 3. Run Full Migration (One Command)
```bash
kaggle2github run-all --user <your_kaggle_username> --github-user <your_github_username>
```

> 🌐 **Public by Default**: All repositories are published as **Public** on your GitHub profile so they immediately showcase on your profile, resume, and portfolio!
> *(Prefer private? Simply add the `--private` flag).*

---

## 🔑 Authentication Details

### Quickest Method: Local `.env` File (Recommended)
Copy [.env.example](.env.example) to `.env` in the repository root and fill in your keys:
```bash
cp .env.example .env
```
*(On Windows PowerShell: `Copy-Item .env.example .env`)*

Inside `.env`:
```ini
KAGGLE_USERNAME=your_kaggle_username
KAGGLE_KEY=your_kaggle_api_key
GITHUB_TOKEN=ghp_your_github_token
```
`kaggle2github` automatically loads this `.env` file whenever you run commands. To switch accounts, simply change the values in `.env` or run `kaggle2github setup --reconfigure`.

---

### Alternative: Manual System Setup

If you prefer system-wide setup instead of `.env`:

#### Kaggle API Setup
1. Log in to [Kaggle](https://www.kaggle.com) and go to your [Account Settings](https://www.kaggle.com/settings).
2. Scroll to the **API** section and click **"Create New Token"**. This downloads `kaggle.json`.
3. Place `kaggle.json` in the `.kaggle` folder in your home directory:
   - **Windows (PowerShell)**:
     ```powershell
     New-Item -ItemType Directory -Force "$HOME\.kaggle"
     Move-Item "$HOME\Downloads\kaggle.json" "$HOME\.kaggle\kaggle.json"
     ```
   - **macOS / Linux**:
     ```bash
     mkdir -p ~/.kaggle
     mv ~/Downloads/kaggle.json ~/.kaggle/kaggle.json
     chmod 600 ~/.kaggle/kaggle.json
     ```

#### GitHub Token Setup
1. Generate a Personal Access Token (classic) with **`repo`** scope at [GitHub Token Settings](https://github.com/settings/tokens/new?scopes=repo&description=kaggle2github).
2. Set the token in your terminal:
   - **Windows (PowerShell)**:
     ```powershell
     $env:GITHUB_TOKEN="ghp_yourTokenHere"
     ```
   - **macOS / Linux**:
     ```bash
     export GITHUB_TOKEN="ghp_yourTokenHere"
     ```

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
