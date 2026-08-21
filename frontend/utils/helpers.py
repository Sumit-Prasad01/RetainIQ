"""Data transformation, validation, formatting, and caching helpers for the RetainIQ Frontend."""

import io
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import streamlit as st

from frontend.config import (
    ACCOUNTS_DATA_PATH,
    DEMOGRAPHIC_DATA_PATH,
    GEOGRAPHY_OPTIONS,
    GENDER_OPTIONS,
    LOCATION_DATA_PATH,
)


def format_currency(value: float) -> str:
    """Format float into USD currency string."""
    try:
        return f"${value:,.2f}"
    except (ValueError, TypeError):
        return f"${value}"


def format_percent(value: float) -> str:
    """Format float [0, 1] into percentage string."""
    try:
        return f"{value * 100:.1f}%"
    except (ValueError, TypeError):
        return f"{value}%"


@st.cache_data(show_spinner=False)
def load_historical_data() -> Optional[pd.DataFrame]:
    """Load and merge historical accounts, demographic, and location datasets."""
    try:
        if not (ACCOUNTS_DATA_PATH.exists() and DEMOGRAPHIC_DATA_PATH.exists() and LOCATION_DATA_PATH.exists()):
            return None

        accounts_df = pd.read_csv(ACCOUNTS_DATA_PATH)
        demographic_df = pd.read_csv(DEMOGRAPHIC_DATA_PATH)
        location_df = pd.read_csv(LOCATION_DATA_PATH)

        # Standardize column casing
        accounts_df.columns = [c.strip() for c in accounts_df.columns]
        demographic_df.columns = [c.strip() for c in demographic_df.columns]
        location_df.columns = [c.strip() for c in location_df.columns]

        # Merge datasets on CustomerId and LocationId
        merged = demographic_df.merge(accounts_df, on="CustomerId", how="inner")
        merged = merged.merge(location_df, on="LocationId", how="inner")

        # Standardize feature names
        merged.rename(
            columns={
                "Gender": "gender",
                "Age": "age",
                "Salary": "salary",
                "Geography": "geography",
                "Tenure": "tenure",
                "Balance": "balance",
                "NumProducts": "numproducts",
                "HasCreditCard": "hascreditcard",
                "IsActive": "isactive",
                "Churned": "churned",
            },
            inplace=True,
        )

        merged["hascreditcard"] = merged["hascreditcard"].astype(bool)
        merged["isactive"] = merged["isactive"].astype(bool)
        merged["balancesalaryratio"] = merged["balance"] / merged["salary"].replace(0, 1)
        merged["tenurebyage"] = merged["tenure"] / merged["age"].replace(0, 1)

        return merged
    except Exception as exc:
        st.warning(f"Unable to load historical dataset: {exc}")
        return None


def generate_csv_template() -> bytes:
    """Generate a downloadable CSV template for batch prediction."""
    sample_data = [
        {
            "gender": "Female",
            "age": 42,
            "salary": 101348.88,
            "geography": "France",
            "tenure": 2,
            "balance": 119827.49,
            "numproducts": 1,
            "hascreditcard": 1,
            "isactive": 1,
        },
        {
            "gender": "Female",
            "age": 55,
            "salary": 82000.00,
            "geography": "Germany",
            "tenure": 1,
            "balance": 145000.00,
            "numproducts": 1,
            "hascreditcard": 1,
            "isactive": 0,
        },
        {
            "gender": "Male",
            "age": 34,
            "salary": 115000.00,
            "geography": "France",
            "tenure": 6,
            "balance": 88000.00,
            "numproducts": 2,
            "hascreditcard": 1,
            "isactive": 1,
        },
    ]
    df = pd.DataFrame(sample_data)
    buffer = io.StringIO()
    df.to_csv(buffer, index=False)
    return buffer.getvalue().encode("utf-8")


def generate_sample_batch_dataset(n: int = 50) -> pd.DataFrame:
    """Extract a sample slice from historical data for one-click batch testing."""
    data = load_historical_data()
    if data is not None and len(data) >= n:
        sample = data.sample(n=n, random_state=42).copy()
        cols = [
            "gender",
            "age",
            "salary",
            "geography",
            "tenure",
            "balance",
            "numproducts",
            "hascreditcard",
            "isactive",
        ]
        return sample[cols].reset_index(drop=True)
    
    # Fallback synthetics if file unavailable
    return pd.DataFrame([
        {
            "gender": "Female",
            "age": 45,
            "salary": 90000.0,
            "geography": "Germany",
            "tenure": 2,
            "balance": 120000.0,
            "numproducts": 1,
            "hascreditcard": True,
            "isactive": False,
        },
        {
            "gender": "Male",
            "age": 30,
            "salary": 65000.0,
            "geography": "France",
            "tenure": 5,
            "balance": 50000.0,
            "numproducts": 2,
            "hascreditcard": True,
            "isactive": True,
        },
    ])


def validate_batch_dataframe(df: pd.DataFrame) -> Tuple[Optional[pd.DataFrame], List[str]]:
    """Validate and sanitize uploaded DataFrame for batch prediction."""
    errors: List[str] = []
    
    # Normalize column names (lowercase & stripped)
    df.columns = [str(c).strip().lower().replace(" ", "").replace("_", "") for c in df.columns]

    # Map standard expected keys
    expected_mapping = {
        "gender": "gender",
        "age": "age",
        "salary": "salary",
        "geography": "geography",
        "tenure": "tenure",
        "balance": "balance",
        "numproducts": "numproducts",
        "products": "numproducts",
        "hascreditcard": "hascreditcard",
        "creditcard": "hascreditcard",
        "isactive": "isactive",
        "active": "isactive",
    }

    renamed_cols = {}
    for col in df.columns:
        if col in expected_mapping:
            renamed_cols[col] = expected_mapping[col]

    df = df.rename(columns=renamed_cols)

    required_fields = [
        "gender",
        "age",
        "salary",
        "geography",
        "tenure",
        "balance",
        "numproducts",
        "hascreditcard",
        "isactive",
    ]

    missing = [f for f in required_fields if f not in df.columns]
    if missing:
        errors.append(f"Missing required columns: {', '.join(missing)}")
        return None, errors

    clean_df = df[required_fields].copy()

    # Clean & Cast Data
    try:
        clean_df["gender"] = clean_df["gender"].astype(str).str.strip().str.capitalize()
        clean_df["geography"] = clean_df["geography"].astype(str).str.strip()
        
        # Normalize geography casing
        geo_map = {g.lower(): g for g in GEOGRAPHY_OPTIONS}
        clean_df["geography"] = clean_df["geography"].apply(lambda x: geo_map.get(x.lower(), x))

        clean_df["age"] = pd.to_numeric(clean_df["age"], errors="coerce").fillna(40).astype(int)
        clean_df["salary"] = pd.to_numeric(clean_df["salary"], errors="coerce").fillna(50000.0).astype(float)
        clean_df["tenure"] = pd.to_numeric(clean_df["tenure"], errors="coerce").fillna(3).astype(int)
        clean_df["balance"] = pd.to_numeric(clean_df["balance"], errors="coerce").fillna(0.0).astype(float)
        clean_df["numproducts"] = pd.to_numeric(clean_df["numproducts"], errors="coerce").fillna(1).astype(int)

        # Boolean conversion
        def parse_bool(val: Any) -> bool:
            if isinstance(val, bool):
                return val
            if isinstance(val, (int, float)):
                return val > 0
            s = str(val).strip().lower()
            return s in ["true", "1", "yes", "y", "t"]

        clean_df["hascreditcard"] = clean_df["hascreditcard"].apply(parse_bool)
        clean_df["isactive"] = clean_df["isactive"].apply(parse_bool)

        # Boundary checks
        invalid_gender = clean_df[~clean_df["gender"].isin(GENDER_OPTIONS)]
        if len(invalid_gender) > 0:
            errors.append(f"Found {len(invalid_gender)} rows with invalid gender. Allowed: Female, Male.")

        invalid_geo = clean_df[~clean_df["geography"].isin(GEOGRAPHY_OPTIONS)]
        if len(invalid_geo) > 0:
            errors.append(f"Found {len(invalid_geo)} rows with invalid geography. Allowed: {', '.join(GEOGRAPHY_OPTIONS)}.")

        clean_df["age"] = clean_df["age"].clip(18, 100)
        clean_df["numproducts"] = clean_df["numproducts"].clip(1, 4)
        clean_df["tenure"] = clean_df["tenure"].clip(0, 50)
        clean_df["salary"] = clean_df["salary"].clip(lower=0.0)
        clean_df["balance"] = clean_df["balance"].clip(lower=0.0)

    except Exception as exc:
        errors.append(f"Data type parsing error: {exc}")
        return None, errors

    if errors:
        return None, errors

    return clean_df, []


def extract_risk_drivers(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Analyze customer payload and identify key churn risk contributing factors."""
    drivers = []

    # Inactivity Driver
    if not payload.get("isactive", True):
        drivers.append({
            "factor": "Account Inactivity",
            "impact": "High Risk (+22%)",
            "type": "negative",
            "detail": "Customer has zero recent banking transactions or digital log-ins.",
        })
    else:
        drivers.append({
            "factor": "Active Engagement",
            "impact": "Loyalty Anchor (-15%)",
            "type": "positive",
            "detail": "Regular account usage and transactions correlate strongly with retention.",
        })

    # Age Risk
    age = payload.get("age", 40)
    if age >= 50:
        drivers.append({
            "factor": f"Senior Demographic (Age {age})",
            "impact": "High Risk (+18%)",
            "type": "negative",
            "detail": "Customers aged 48-65 show 2.5x higher churn rates in this portfolio.",
        })
    elif age <= 32:
        drivers.append({
            "factor": f"Young Demographic (Age {age})",
            "impact": "Low Risk (-8%)",
            "type": "positive",
            "detail": "Younger cohorts demonstrate higher digital stickiness and lower attrition.",
        })

    # Geography
    geo = payload.get("geography", "")
    if geo == "Germany":
        drivers.append({
            "factor": "Regional Market: Germany",
            "impact": "Elevated Risk (+16%)",
            "type": "negative",
            "detail": "German customer segment historically shows a 32% baseline churn rate.",
        })
    elif geo == "France":
        drivers.append({
            "factor": "Regional Market: France",
            "impact": "Stable Baseline (-6%)",
            "type": "positive",
            "detail": "France represents the largest and most stable retention market.",
        })

    # Number of Products
    num_products = payload.get("numproducts", 1)
    if num_products == 1:
        drivers.append({
            "factor": "Single Product Relationship",
            "impact": "Moderate Risk (+12%)",
            "type": "negative",
            "detail": "Holding only 1 product makes switching to a competitor effortless.",
        })
    elif num_products == 2:
        drivers.append({
            "factor": "Optimal Multi-Product (2 Products)",
            "impact": "Strong Loyalty Anchor (-25%)",
            "type": "positive",
            "detail": "Customers with exactly 2 products exhibit the lowest churn rate (under 8%).",
        })
    elif num_products >= 3:
        drivers.append({
            "factor": f"Complex Multi-Product ({num_products} Products)",
            "impact": "Critical Risk (+30%)",
            "type": "negative",
            "detail": "Customers with 3+ products frequently experience fee friction and service fatigue.",
        })

    # Balance to Salary
    balance = payload.get("balance", 0.0)
    salary = payload.get("salary", 1.0)
    ratio = balance / max(salary, 1.0)
    if ratio > 1.5 and balance > 100000:
        drivers.append({
            "factor": "High Liquidity Deposit Exposure",
            "impact": "Flight Risk (+14%)",
            "type": "negative",
            "detail": f"Substantial deposit balance ({format_currency(balance)}) is sensitive to rate shopping.",
        })

    return drivers
