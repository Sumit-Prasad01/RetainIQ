"""Exploratory Data Analysis and Historical Portfolio Churn Insights View."""

import streamlit as st

from frontend.components.cards import render_kpi_card
from frontend.components.charts import render_historical_eda_charts
from frontend.utils.helpers import format_currency, format_percent, load_historical_data
from frontend.utils.styling import render_html


def render_customer_insights_view() -> None:
    """Render historical portfolio exploratory data analysis and banking insights."""
    st.markdown("## 📈 Historical Portfolio Churn Insights & EDA")
    st.caption("Explore behavioral patterns, demographic drivers, and financial correlations from the 10,000-customer historical baseline.")

    df = load_historical_data()
    if df is None or len(df) == 0:
        st.warning("Historical dataset not found in `artifacts/processed_data/`. Please ensure data artifacts are present.")
        return

    # Filter Sidebar/Expander
    with st.expander("🔍 Interactive Data Filters", expanded=False):
        f_c1, f_c2, f_c3 = st.columns(3)
        with f_c1:
            all_geos = sorted(df["geography"].unique())
            selected_geos = st.multiselect("Geography", options=all_geos, default=all_geos)
        with f_c2:
            all_genders = sorted(df["gender"].unique())
            selected_genders = st.multiselect("Gender", options=all_genders, default=all_genders)
        with f_c3:
            min_age, max_age = int(df["age"].min()), int(df["age"].max())
            age_range = st.slider("Age Range", min_value=min_age, max_value=max_age, value=(min_age, max_age))

    filtered_df = df[
        (df["geography"].isin(selected_geos))
        & (df["gender"].isin(selected_genders))
        & (df["age"].between(age_range[0], age_range[1]))
    ]

    # Portfolio KPI Summary
    total_cust = len(filtered_df)
    churn_count = int(filtered_df["churned"].sum())
    churn_rate = churn_count / max(total_cust, 1)
    total_balance = filtered_df["balance"].sum()
    active_rate = filtered_df["isactive"].mean()

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        render_kpi_card("Cohort Size", f"{total_cust:,}", f"{(total_cust/len(df))*100:.1f}% of total portfolio", "#6366F1", "👥")
    with k2:
        render_kpi_card("Cohort Churn Rate", format_percent(churn_rate), f"{churn_count:,} churned accounts", "#EF4444", "📉")
    with k3:
        render_kpi_card("Total Deposit Assets", format_currency(total_balance), f"Avg: {format_currency(filtered_df['balance'].mean())}", "#10B981", "🏦")
    with k4:
        render_kpi_card("Active Engagement %", format_percent(active_rate), "Digital / Branch active", "#F59E0B", "⚡")

    st.markdown("---")

    # Multi-tab Visualizations
    render_historical_eda_charts(filtered_df)

    # Executive Insights & Takeaways Callout
    st.markdown("---")
    st.markdown("### 💡 Key Strategic Retention Takeaways")

    col1, col2 = st.columns(2)
    with col1:
        render_html(
            """
            <div style="background: rgba(30, 41, 59, 0.5); border-left: 4px solid #6366F1; padding: 14px 18px; border-radius: 0 8px 8px 0; margin-bottom: 12px;">
                <div style="font-weight: 700; color: #f8fafc; font-size: 0.95rem;">🎯 The "2-Product" Sweet Spot</div>
                <div style="font-size: 0.84rem; color: #94a3b8; margin-top: 4px;">
                    Customers holding exactly <b>2 products</b> exhibit the lowest churn rate (<b>~7.6%</b>). Holding 1 product yields <b>27.7%</b> churn, while customers holding 3 or 4 products exceed <b>80%</b> churn due to fee complexity and product friction.
                </div>
            </div>
            """
        )

    with col2:
        render_html(
            """
            <div style="background: rgba(30, 41, 59, 0.5); border-left: 4px solid #EF4444; padding: 14px 18px; border-radius: 0 8px 8px 0; margin-bottom: 12px;">
                <div style="font-weight: 700; color: #f8fafc; font-size: 0.95rem;">🇩🇪 German Market Outlier Risk</div>
                <div style="font-size: 0.84rem; color: #94a3b8; margin-top: 4px;">
                    German banking customers experience a baseline churn rate of <b>32.4%</b>, significantly higher than France (<b>16.1%</b>) or Spain (<b>16.7%</b>). Local fintech competition and interest rate sensitivity necessitate dedicated German retention packages.
                </div>
            </div>
            """
        )
