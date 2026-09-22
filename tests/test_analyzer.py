"""
Unit tests for analyzer.py (magic stripping, AST import extraction, path rewriting).
"""

from kaggle2github.analyzer import (
    clean_notebook_cells,
    extract_imports_from_code,
)

def test_clean_notebook_cells_strips_magics():
    nb_data = {
        "cells": [
            {
                "cell_type": "code",
                "source": [
                    "!pip install -q xgboost\n",
                    "%matplotlib inline\n",
                    "import pandas as pd\n",
                    "df = pd.read_csv('/kaggle/input/house-prices/train.csv')\n",
                ],
            }
        ]
    }
    clean_code, _ = clean_notebook_cells(nb_data)

    assert "# !pip install -q xgboost" in clean_code
    assert "# %matplotlib inline" in clean_code
    assert 'df = pd.read_csv(_resolve_data_path("house-prices/train.csv"))' in clean_code

def test_extract_imports_from_code():
    code = """
import os
import sys
import json
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import cv2
from PIL import Image
import xgboost as xgb
"""
    packages = extract_imports_from_code(code)

    # Standard library modules should be excluded
    assert "os" not in packages
    assert "sys" not in packages
    assert "json" not in packages

    # PyPI mappings
    assert "numpy" in packages
    assert "pandas" in packages
    assert "scikit-learn" in packages
    assert "opencv-python" in packages
    assert "pillow" in packages
    assert "xgboost" in packages
