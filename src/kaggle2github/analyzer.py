"""
Notebook analysis, AST import extraction, magic stripping, and code extraction.
"""

import ast
import json
import os
import re
import sys
from typing import Dict, List, Set, Tuple

# Mapping of common Python import names to their PyPI package distribution names
IMPORT_TO_PYPI = {
    "sklearn": "scikit-learn",
    "cv2": "opencv-python",
    "PIL": "pillow",
    "yaml": "pyyaml",
    "bs4": "beautifulsoup4",
    "yt_dlp": "yt-dlp",
    "torch": "torch",
    "torchvision": "torchvision",
    "torchaudio": "torchaudio",
    "tensorflow": "tensorflow",
    "keras": "keras",
    "xgboost": "xgboost",
    "catboost": "catboost",
    "lightgbm": "lightgbm",
    "seaborn": "seaborn",
    "matplotlib": "matplotlib",
    "pandas": "pandas",
    "numpy": "numpy",
    "scipy": "scipy",
    "nltk": "nltk",
    "transformers": "transformers",
    "datasets": "datasets",
    "optuna": "optuna",
    "tqdm": "tqdm",
    "fastai": "fastai",
    "albumentations": "albumentations",
    "sentence_transformers": "sentence-transformers",
    "ultralytics": "ultralytics",
    "yellowbrick": "yellowbrick",
    "spacy": "spacy",
    "gensim": "gensim",
    "plotly": "plotly",
    "statsmodels": "statsmodels",
    "networkx": "networkx",
    "google": "google-generativeai",
}

# Standard library modules (Python 3.9+) to exclude from requirements.txt
STDLIB_MODULES = {
    "abc", "argparse", "array", "ast", "asyncio", "base64", "binascii",
    "bisect", "builtins", "bz2", "calendar", "cgi", "cmath", "collections",
    "concurrent", "configparser", "contextlib", "copy", "csv", "ctypes",
    "dataclasses", "datetime", "decimal", "difflib", "dis", "distutils",
    "doctest", "email", "enum", "errno", "faulthandler", "fcntl", "filecmp",
    "fileinput", "fnmatch", "fractions", "functools", "gc", "getopt",
    "getpass", "gettext", "glob", "gzip", "hashlib", "heapq", "hmac",
    "html", "http", "imaplib", "imghdr", "importlib", "inspect", "io",
    "ipaddress", "itertools", "json", "keyword", "linecache", "locale",
    "logging", "lzma", "mailbox", "mailcap", "marshal", "math", "mimetypes",
    "mmap", "modulefinder", "multiprocessing", "netrc", "nntplib", "numbers",
    "operator", "optparse", "os", "parser", "pathlib", "pdb", "pickle",
    "pickletools", "pkgutil", "platform", "plistlib", "poplib", "posix",
    "posixpath", "pprint", "profile", "pstats", "pty", "pwd", "py_compile",
    "pyclbr", "pydoc", "queue", "quopri", "random", "re", "reprlib",
    "resource", "rlcompleter", "runpy", "sched", "secrets", "select",
    "selectors", "shelve", "shlex", "shutil", "signal", "site", "smtpd",
    "smtplib", "sndhdr", "socket", "socketserver", "spwd", "sqlite3",
    "ssl", "stat", "statistics", "string", "stringprep", "struct",
    "subprocess", "sunau", "symbol", "symtable", "sys", "sysconfig",
    "tabnanny", "tarfile", "telnetlib", "tempfile", "termios", "test",
    "textwrap", "threading", "time", "timeit", "tkinter", "token",
    "tokenize", "trace", "traceback", "tracemalloc", "tty", "turtle",
    "turtledemo", "types", "typing", "unicodedata", "unittest", "urllib",
    "uu", "uuid", "venv", "warnings", "wave", "weakref", "webbrowser",
    "wsgiref", "xdrlib", "xml", "xmlrpc", "zipapp", "zipfile", "zipimport",
    "zlib", "_thread"
}

def clean_notebook_cells(nb_data: dict) -> Tuple[str, List[str]]:
    """
    Extracts code from notebook cells, stripping shell/magic commands (! and %)
    and converting Kaggle input paths to smart resolver lookups.
    Returns (clean_code_str, raw_lines_list).
    """
    code_cells = [c for c in nb_data.get("cells", []) if c.get("cell_type") == "code"]
    clean_lines = []
    
    for idx, cell in enumerate(code_cells):
        src = cell.get("source", [])
        if isinstance(src, str):
            lines = src.splitlines(keepends=True)
        else:
            lines = src
            
        cell_has_content = False
        cell_lines = []
        for line in lines:
            stripped = line.strip()
            # Comment out shell or ipython magic
            if stripped.startswith("!") or stripped.startswith("%"):
                cell_lines.append(f"# {line.rstrip()}\n")
            else:
                # Wrap /kaggle/input/ file paths with _resolve_data_path(...)
                processed_line = re.sub(
                    r"([\"'])(?:/kaggle/input/|\.\./input/)([^\"']+)\1",
                    r'_resolve_data_path("\2")',
                    line
                )
                if not processed_line.endswith("\n"):
                    processed_line += "\n"
                cell_lines.append(processed_line)
                if stripped and not stripped.startswith("#"):
                    cell_has_content = True

        if cell_has_content:
            clean_lines.append(f"\n# --- Cell {idx + 1} ---\n")
            clean_lines.extend(cell_lines)

    return "".join(clean_lines), clean_lines

def extract_imports_from_code(code: str) -> List[str]:
    """
    Uses AST to parse Python code and detect all top-level module imports,
    filtering out standard library packages and mapping to PyPI names.
    """
    modules: Set[str] = set()
    
    # Pre-clean lines to prevent AST syntax errors on commented magics or syntax issues
    valid_code_lines = []
    for line in code.splitlines():
        # Keep non-empty, non-magic lines
        if not line.strip().startswith("# !"):
            valid_code_lines.append(line)
    
    source = "\n".join(valid_code_lines)
    try:
        tree = ast.parse(source)
    except SyntaxError:
        # Fallback to regex if full file has a syntax error
        for line in source.splitlines():
            line_str = line.strip()
            m1 = re.match(r"^import\s+([a-zA-Z0-9_\.]+)", line_str)
            m2 = re.match(r"^from\s+([a-zA-Z0-9_\.]+)\s+import", line_str)
            if m1:
                modules.add(m1.group(1).split(".")[0])
            elif m2:
                modules.add(m2.group(1).split(".")[0])
        tree = None

    if tree is not None:
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    top_module = alias.name.split(".")[0]
                    modules.add(top_module)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    top_module = node.module.split(".")[0]
                    modules.add(top_module)

    # Filter out standard library modules and internal references
    pypi_packages = set()
    for mod in modules:
        if mod in STDLIB_MODULES or not mod or mod.startswith("_"):
            continue
        pypi_name = IMPORT_TO_PYPI.get(mod, mod.lower())
        pypi_packages.add(pypi_name)

    return sorted(list(pypi_packages))

def analyze_notebook(nb_path: str) -> Dict:
    """
    Analyzes a notebook file, returning clean code, dependencies, and cell metrics.
    """
    with open(nb_path, "r", encoding="utf-8", errors="ignore") as f:
        nb_data = json.load(f)

    clean_code, _ = clean_notebook_cells(nb_data)
    dependencies = extract_imports_from_code(clean_code)

    code_cells = [c for c in nb_data.get("cells", []) if c.get("cell_type") == "code"]
    markdown_cells = [c for c in nb_data.get("cells", []) if c.get("cell_type") == "markdown"]

    return {
        "total_cells": len(nb_data.get("cells", [])),
        "code_cells_count": len(code_cells),
        "markdown_cells_count": len(markdown_cells),
        "clean_code": clean_code,
        "dependencies": dependencies,
    }
