"""Configuration settings and constants for the RetainIQ Streamlit Frontend."""

import os
from pathlib import Path
from typing import Any, Dict, List

# Workspace Root
ROOT_DIR = Path(__file__).resolve().parents[1]

# Default API Configuration
DEFAULT_API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")
DEFAULT_API_USERNAME = os.getenv("API_USERNAME", "admin")
DEFAULT_API_PASSWORD = os.getenv("API_PASSWORD", "change-me")

# Data Artifact Paths (for EDA / benchmark insights)
ACCOUNTS_DATA_PATH = ROOT_DIR / "artifacts" / "processed_data" / "accounts.csv"
DEMOGRAPHIC_DATA_PATH = ROOT_DIR / "artifacts" / "processed_data" / "demographic.csv"
LOCATION_DATA_PATH = ROOT_DIR / "artifacts" / "processed_data" / "location.csv"
MODEL_PATH = ROOT_DIR / "artifacts" / "models" / "lgbm_model.pkl"

# Allowed Categorical Values
GEOGRAPHY_OPTIONS: List[str] = ["Canada", "France", "Germany", "Spain", "UK", "USA"]
GENDER_OPTIONS: List[str] = ["Female", "Male"]
NUM_PRODUCTS_OPTIONS: List[int] = [1, 2, 3, 4]

# Preset Customer Profiles for One-Click Testing
PRESET_PROFILES: Dict[str, Dict[str, Any]] = {
    "Custom Profile": {
        "gender": "Female",
        "age": 42,
        "salary": 101348.88,
        "geography": "France",
        "tenure": 2,
        "balance": 119827.49,
        "numproducts": 1,
        "hascreditcard": True,
        "isactive": True,
    },
    "High-Risk Senior Inactive (Germany)": {
        "gender": "Female",
        "age": 55,
        "salary": 82000.0,
        "geography": "Germany",
        "tenure": 1,
        "balance": 145000.0,
        "numproducts": 1,
        "hascreditcard": True,
        "isactive": False,
    },
    "Loyal Prime Customer (France)": {
        "gender": "Male",
        "age": 34,
        "salary": 115000.0,
        "geography": "France",
        "tenure": 6,
        "balance": 88000.0,
        "numproducts": 2,
        "hascreditcard": True,
        "isactive": True,
    },
    "Affluent At-Risk Inactive (UK)": {
        "gender": "Male",
        "age": 50,
        "salary": 145000.0,
        "geography": "UK",
        "tenure": 3,
        "balance": 178000.0,
        "numproducts": 1,
        "hascreditcard": False,
        "isactive": False,
    },
    "Young Starter (Spain)": {
        "gender": "Female",
        "age": 25,
        "salary": 58000.0,
        "geography": "Spain",
        "tenure": 2,
        "balance": 35000.0,
        "numproducts": 2,
        "hascreditcard": True,
        "isactive": True,
    },
    "Multi-Product Complex Case (Canada)": {
        "gender": "Male",
        "age": 45,
        "salary": 92000.0,
        "geography": "Canada",
        "tenure": 5,
        "balance": 125000.0,
        "numproducts": 3,
        "hascreditcard": True,
        "isactive": False,
    },
}

# Risk Tier Definitions
def get_risk_tier(probability: float) -> Dict[str, Any]:
    """Return risk classification metadata given churn probability."""
    if probability < 0.20:
        return {
            "tier": "Low Risk",
            "color": "#10B981",  # Emerald Green
            "badge_class": "badge-low",
            "icon": "🟢",
            "summary": "Customer exhibits strong loyalty signals and high engagement.",
        }
    elif probability < 0.35:
        return {
            "tier": "Moderate Risk",
            "color": "#F59E0B",  # Amber
            "badge_class": "badge-medium",
            "icon": "🟡",
            "summary": "Customer exhibits early warning signs. Proactive engagement recommended.",
        }
    elif probability < 0.60:
        return {
            "tier": "High Risk",
            "color": "#F97316",  # Orange
            "badge_class": "badge-high",
            "icon": "🟠",
            "summary": "Significant churn probability detected. Urgent retention action advised.",
        }
    else:
        return {
            "tier": "Critical Risk",
            "color": "#EF4444",  # Crimson Red
            "badge_class": "badge-critical",
            "icon": "🔴",
            "summary": "Immediate flight risk. Personalized executive intervention required.",
        }
