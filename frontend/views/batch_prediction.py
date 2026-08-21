"""Batch Customer Scoring, Portfolio Risk Analytics and CSV Export View."""

import io
from typing import Any, Dict, List
import pandas as pd
import streamlit as st

from frontend.components.cards import render_kpi_card
from frontend.components.charts import render_batch_analytics_charts
from frontend.config import get_risk_tier
from frontend.utils.helpers import (
    format_currency,
    format_percent,
    generate_csv_template,
    generate_sample_batch_dataset,
    validate_batch_dataframe,
)


def render_batch_prediction_view(
    api_client: Any,
    custom_threshold: float,
    force_local: bool = False,
) -> None:
    """Render batch CSV upload, inference execution, summary KPIs, and export controls."""
    st.markdown("## 📊 Batch Portfolio Churn Risk Scoring")
    st.caption("Upload a portfolio of customer profiles to compute batch churn probabilities, identify flight risks, and export scored cohorts.")

    # Template download and demo sample loader row
    top_col1, top_col2, top_col3 = st.columns([1.5, 1.5, 2])

    with top_col1:
        st.download_button(
            label="📥 Download CSV Template",
            data=generate_csv_template(),
            file_name="retainiq_batch_template.csv",
            mime="text/csv",
            use_container_width=True,
            help="Download standard CSV header format required for batch predictions",
        )

    with top_col2:
        if st.button("🎲 Load 50 Sample Customers", use_container_width=True, help="Load 50 real customer records for instant batch testing"):
            sample_df = generate_sample_batch_dataset(n=50)
            st.session_state["batch_input_df"] = sample_df
            st.session_state.pop("batch_scored_df", None)
            st.toast("Loaded 50 sample customers!", icon="📂")

    uploaded_file = st.file_uploader(
        "Upload Customer Batch CSV",
        type=["csv"],
        help="Upload CSV file with columns: gender, age, salary, geography, tenure, balance, numproducts, hascreditcard, isactive",
    )

    if uploaded_file is not None:
        try:
            raw_df = pd.read_csv(uploaded_file)
            st.session_state["batch_input_df"] = raw_df
            st.session_state.pop("batch_scored_df", None)
        except Exception as exc:
            st.error(f"Error reading uploaded CSV: {exc}")
            return

    input_df = st.session_state.get("batch_input_df")

    if input_df is not None:
        st.markdown("---")
        st.markdown(f"### 📄 Batch Data Preview ({len(input_df)} records)")

        clean_df, errors = validate_batch_dataframe(input_df)
        if errors:
            for err in errors:
                st.error(f"⚠️ Validation Error: {err}")
            return

        st.dataframe(clean_df.head(10), use_container_width=True)

        # Batch Run Button
        run_batch = st.button("🚀 Run Batch Churn Scoring", type="primary", use_container_width=True)

        if run_batch:
            records = clean_df.to_dict(orient="records")
            progress_bar = st.progress(0, text="Initializing batch scoring...")

            def update_progress(curr: int, total: int) -> None:
                pct = int((curr / total) * 100)
                progress_bar.progress(pct, text=f"Scoring customer {curr} of {total} ({pct}%)...")

            if force_local:
                # Direct in-memory scoring
                results: List[Dict[str, Any]] = []
                for idx, rec in enumerate(records):
                    res = api_client.predict_direct(rec)
                    results.append(res)
                    update_progress(idx + 1, len(records))
                summary = {
                    "total": len(records),
                    "successful": len(records),
                    "failed": 0,
                    "cache_hits": 0,
                    "cache_misses": 0,
                    "avg_latency_ms": 1.2,
                }
            else:
                results, summary = api_client.predict_batch(
                    records,
                    progress_callback=update_progress,
                    allow_fallback=True,
                )

            progress_bar.empty()

            # Compile Scored DataFrame
            scored_df = clean_df.copy()
            scored_df["churn_probability"] = [round(r.get("churn_probability", 0.0), 4) for r in results]
            scored_df["churn_flag"] = scored_df["churn_probability"] >= custom_threshold
            scored_df["churn_verdict"] = scored_df["churn_flag"].map({True: "Churn Risk", False: "Retained"})
            scored_df["risk_tier"] = scored_df["churn_probability"].apply(lambda p: get_risk_tier(p)["tier"])
            scored_df["cache_status"] = [r.get("cache_status", "n/a") for r in results]

            st.session_state["batch_scored_df"] = scored_df
            st.session_state["batch_summary"] = summary
            st.toast("Batch scoring completed successfully!", icon="✅")

    # Display Scored Results
    if "batch_scored_df" in st.session_state:
        scored_df = st.session_state["batch_scored_df"]
        summary = st.session_state.get("batch_summary", {})

        st.markdown("---")
        st.markdown("### 📈 Batch Risk Portfolio Summary")

        total_customers = len(scored_df)
        churn_count = int(scored_df["churn_flag"].sum())
        churn_rate = churn_count / max(total_customers, 1)
        total_balance_at_risk = scored_df[scored_df["churn_flag"]]["balance"].sum()
        avg_prob = scored_df["churn_probability"].mean()

        # KPI Metrics Grid
        k1, k2, k3, k4 = st.columns(4)
        with k1:
            render_kpi_card("Total Evaluated", f"{total_customers:,}", "Customer accounts", "#6366F1", "👥")
        with k2:
            render_kpi_card("Flagged Churn Rate", format_percent(churn_rate), f"{churn_count} at-risk accounts", "#EF4444", "⚠️")
        with k3:
            render_kpi_card("Balance Exposure", format_currency(total_balance_at_risk), "Deposits at flight risk", "#F59E0B", "💸")
        with k4:
            render_kpi_card("Avg Churn Probability", format_percent(avg_prob), f"Cutoff: {custom_threshold:.2f}", "#38BDF8", "🎯")

        # Distribution Visualizations
        st.markdown("---")
        render_batch_analytics_charts(scored_df, custom_threshold)

        # Filterable Results Table
        st.markdown("---")
        st.markdown("### 🔍 Scored Customer Portfolio Explorer")

        f_col1, f_col2 = st.columns([2, 2])
        with f_col1:
            tier_filter = st.multiselect(
                "Filter by Risk Tier",
                options=["Critical Risk", "High Risk", "Moderate Risk", "Low Risk"],
                default=["Critical Risk", "High Risk", "Moderate Risk", "Low Risk"],
            )
        with f_col2:
            verdict_filter = st.multiselect(
                "Filter by Verdict",
                options=["Churn Risk", "Retained"],
                default=["Churn Risk", "Retained"],
            )

        filtered_df = scored_df[
            scored_df["risk_tier"].isin(tier_filter) & scored_df["churn_verdict"].isin(verdict_filter)
        ]

        st.dataframe(
            filtered_df,
            use_container_width=True,
            column_config={
                "churn_probability": st.column_config.ProgressColumn(
                    "Churn Risk %",
                    format="%.2f",
                    min_value=0,
                    max_value=1,
                ),
                "balance": st.column_config.NumberColumn("Balance", format="$%.2f"),
                "salary": st.column_config.NumberColumn("Salary", format="$%.2f"),
            },
        )

        # Download Scored CSV
        csv_buffer = io.StringIO()
        scored_df.to_csv(csv_buffer, index=False)
        st.download_button(
            label="💾 Download Scored Results (CSV)",
            data=csv_buffer.getvalue().encode("utf-8"),
            file_name="retainiq_scored_portfolio.csv",
            mime="text/csv",
            type="primary",
            use_container_width=True,
        )
