"""Single Customer Churn Risk Scoring, What-If Simulator and Prescriptive Retention View."""

from typing import Any, Dict
import streamlit as st

from frontend.components.cards import (
    render_kpi_card,
    render_prediction_banner,
    render_risk_drivers_list,
)
from frontend.components.charts import (
    render_gauge_chart,
    render_whatif_sensitivity_chart,
)
from frontend.components.forms import render_customer_input_form
from frontend.utils.helpers import extract_risk_drivers, format_currency, format_percent
from frontend.utils.retention import generate_retention_playbook
from frontend.utils.styling import render_html


def render_single_prediction_view(
    api_client: Any,
    custom_threshold: float,
    force_local: bool = False,
) -> None:
    """Render the single customer scoring interface, what-if simulator and retention advice."""
    st.markdown("## 🔮 Individual Customer Churn Risk Evaluation")
    st.caption("Evaluate customer attrition probability in real-time, inspect risk signals, and explore retention actions.")

    # Render Profile Input Form
    payload, submitted = render_customer_input_form()

    # Perform prediction if submitted or if already stored
    if submitted or "last_single_prediction" in st.session_state:
        if submitted:
            with st.spinner("Evaluating churn risk via RetainIQ ML Engine..."):
                if force_local:
                    result = api_client.predict_direct(payload)
                else:
                    result = api_client.predict(payload, allow_fallback=True)

                if not result.get("success", False):
                    st.error(f"Prediction failed: {result.get('error')}")
                    return

                st.session_state["last_single_prediction"] = result
                st.session_state["last_payload"] = payload
        else:
            result = st.session_state["last_single_prediction"]
            payload = st.session_state.get("last_payload", payload)

        prob = result.get("churn_probability", 0.0)

        st.markdown("---")
        st.markdown("### 📋 Prediction Assessment & Decision Output")

        # Top Banner Verdict
        render_prediction_banner(result, custom_threshold)

        # Gauge & Summary KPIs Grid
        col_gauge, col_kpis = st.columns([1.2, 1])

        with col_gauge:
            st.markdown("##### 🧭 Attrition Probability Meter")
            render_gauge_chart(prob, custom_threshold)

        with col_kpis:
            st.markdown("##### 📊 Financial Exposure & Metrics")
            render_kpi_card(
                title="Deposit Balance at Risk",
                value=format_currency(payload["balance"]),
                subtitle=f"Annual Salary: {format_currency(payload['salary'])}",
                color="#EF4444" if prob >= custom_threshold else "#10B981",
                icon="💰",
            )
            st.write("")
            render_kpi_card(
                title="Relationship Depth",
                value=f"{payload['numproducts']} Product{'s' if payload['numproducts'] > 1 else ''}",
                subtitle=f"Tenure: {payload['tenure']} Years | {'Active' if payload['isactive'] else 'Inactive'}",
                color="#6366F1",
                icon="🤝",
            )

        # Risk Drivers Analysis
        st.markdown("---")
        drivers = extract_risk_drivers(payload)
        render_risk_drivers_list(drivers)

        # Prescriptive AI Retention Playbook
        st.markdown("---")
        st.markdown("### 🛡️ Prescriptive AI Retention Action Plan")
        playbook = generate_retention_playbook(payload, prob)

        st.info(f"**Retention Urgency Level:** {playbook['urgency_level']}")

        if playbook["urgent_actions"]:
            for act in playbook["urgent_actions"]:
                st.warning(f"⚠️ **Immediate Operational Alert:** {act}")

        for strat in playbook["strategies"]:
            badge_col = "#EF4444" if strat["priority"] == "Critical" else "#F59E0B" if strat["priority"] == "High" else "#6366F1"
            render_html(
                f"""
                <div class="recommendation-card" style="border-left-color: {badge_col};">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                        <span style="font-weight: 700; font-size: 1.05rem; color: #f8fafc;">{strat['title']}</span>
                        <span style="background: rgba(255,255,255,0.08); color: {badge_col}; font-weight: 700; font-size: 0.75rem; padding: 2px 8px; border-radius: 4px;">
                            Priority: {strat['priority']}
                        </span>
                    </div>
                    <div style="font-size: 0.88rem; color: #cbd5e1; margin-bottom: 6px;">{strat['action']}</div>
                    <div style="display: flex; justify-content: space-between; font-size: 0.78rem; color: #94a3b8; border-top: 1px solid rgba(255,255,255,0.06); padding-top: 6px; margin-top: 6px;">
                        <span>📡 <b>Channel:</b> {strat['channel']}</span>
                        <span style="color: #34d399; font-weight: 600;">📈 <b>Impact:</b> {strat['expected_reduction']}</span>
                    </div>
                </div>
                """
            )

        # Interactive Sensitivity & What-If Exploration
        st.markdown("---")
        render_whatif_sensitivity_chart(payload, api_client, custom_threshold)
