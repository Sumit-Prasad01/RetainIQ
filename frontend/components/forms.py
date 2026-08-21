"""Customer profile input forms and preset handlers for single customer inference."""

import random
from typing import Any, Dict, Tuple
import streamlit as st

from frontend.config import (
    GENDER_OPTIONS,
    GEOGRAPHY_OPTIONS,
    NUM_PRODUCTS_OPTIONS,
    PRESET_PROFILES,
)
from frontend.utils.helpers import load_historical_data


def render_customer_input_form() -> Tuple[Dict[str, Any], bool]:
    """Render customer profile input controls with preset templates and validation."""
    st.markdown("### 👤 Customer Profile & Banking Attributes")

    # Preset Profile Selector Row
    p_col1, p_col2 = st.columns([3, 1])
    with p_col1:
        preset_name = st.selectbox(
            "⚡ Quick Load Preset Persona",
            options=list(PRESET_PROFILES.keys()),
            index=0,
            help="Choose a pre-configured banking profile to instantly populate attributes.",
        )
    with p_col2:
        st.write("")
        st.write("")
        load_random = st.button("🎲 Random Customer", help="Sample a real customer record from historical data")

    # Handle preset state changes
    current_preset = PRESET_PROFILES.get(preset_name, PRESET_PROFILES["Custom Profile"])

    if load_random:
        data = load_historical_data()
        if data is not None and len(data) > 0:
            random_row = data.sample(n=1).iloc[0]
            st.session_state["form_gender"] = str(random_row["gender"])
            st.session_state["form_age"] = int(random_row["age"])
            st.session_state["form_salary"] = float(random_row["salary"])
            st.session_state["form_geography"] = str(random_row["geography"])
            st.session_state["form_tenure"] = int(random_row["tenure"])
            st.session_state["form_balance"] = float(random_row["balance"])
            st.session_state["form_numproducts"] = int(random_row["numproducts"])
            st.session_state["form_hascreditcard"] = bool(random_row["hascreditcard"])
            st.session_state["form_isactive"] = bool(random_row["isactive"])
            st.toast("Loaded random historical customer!", icon="🎲")

    elif "last_preset" not in st.session_state or st.session_state["last_preset"] != preset_name:
        st.session_state["last_preset"] = preset_name
        st.session_state["form_gender"] = current_preset["gender"]
        st.session_state["form_age"] = current_preset["age"]
        st.session_state["form_salary"] = current_preset["salary"]
        st.session_state["form_geography"] = current_preset["geography"]
        st.session_state["form_tenure"] = current_preset["tenure"]
        st.session_state["form_balance"] = current_preset["balance"]
        st.session_state["form_numproducts"] = current_preset["numproducts"]
        st.session_state["form_hascreditcard"] = current_preset["hascreditcard"]
        st.session_state["form_isactive"] = current_preset["isactive"]

    # Form Fields in 2 Columns
    with st.form("customer_prediction_form"):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("##### 🌐 Demographics & Location")
            
            gender_val = st.session_state.get("form_gender", "Female")
            gender_idx = GENDER_OPTIONS.index(gender_val) if gender_val in GENDER_OPTIONS else 0
            gender = st.selectbox("Gender", options=GENDER_OPTIONS, index=gender_idx)

            age = st.number_input(
                "Customer Age (Years)",
                min_value=18,
                max_value=100,
                value=int(st.session_state.get("form_age", 42)),
                step=1,
                help="Customer age between 18 and 100",
            )

            geo_val = st.session_state.get("form_geography", "France")
            geo_idx = GEOGRAPHY_OPTIONS.index(geo_val) if geo_val in GEOGRAPHY_OPTIONS else 1
            geography = st.selectbox("Geography / Country", options=GEOGRAPHY_OPTIONS, index=geo_idx)

            salary = st.number_input(
                "Estimated Annual Salary ($)",
                min_value=0.0,
                max_value=1000000.0,
                value=float(st.session_state.get("form_salary", 101348.88)),
                step=1000.0,
                format="%.2f",
            )

        with col2:
            st.markdown("##### 💳 Banking & Account Profile")

            tenure = st.slider(
                "Tenure with Bank (Years)",
                min_value=0,
                max_value=20,
                value=int(st.session_state.get("form_tenure", 2)),
                help="Number of years customer has banked with the institution",
            )

            balance = st.number_input(
                "Current Account Balance ($)",
                min_value=0.0,
                max_value=2000000.0,
                value=float(st.session_state.get("form_balance", 119827.49)),
                step=1000.0,
                format="%.2f",
            )

            prod_val = int(st.session_state.get("form_numproducts", 1))
            prod_idx = NUM_PRODUCTS_OPTIONS.index(prod_val) if prod_val in NUM_PRODUCTS_OPTIONS else 0
            numproducts = st.selectbox(
                "Number of Bank Products Held",
                options=NUM_PRODUCTS_OPTIONS,
                index=prod_idx,
                help="Total active products (Checking, Savings, Credit Line, Mortgage, etc.)",
            )

            b_col1, b_col2 = st.columns(2)
            with b_col1:
                hascreditcard = st.checkbox(
                    "Has Active Credit Card",
                    value=bool(st.session_state.get("form_hascreditcard", True)),
                )
            with b_col2:
                isactive = st.checkbox(
                    "Is Active Member",
                    value=bool(st.session_state.get("form_isactive", True)),
                    help="Active transaction history in the past 30 days",
                )

        submit_btn = st.form_submit_button(
            "⚡ Predict Churn Probability",
            use_container_width=True,
            type="primary",
        )

    payload = {
        "gender": gender,
        "age": int(age),
        "salary": float(salary),
        "geography": geography,
        "tenure": int(tenure),
        "balance": float(balance),
        "numproducts": int(numproducts),
        "hascreditcard": bool(hascreditcard),
        "isactive": bool(isactive),
    }

    return payload, submit_btn
