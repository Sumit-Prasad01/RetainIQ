"""Sidebar navigation and application configuration controls."""

from typing import Any, Dict
import streamlit as st

from frontend.config import (
    DEFAULT_API_PASSWORD,
    DEFAULT_API_URL,
    DEFAULT_API_USERNAME,
)
from frontend.utils.styling import render_html


def render_sidebar(api_client: Any) -> Dict[str, Any]:
    """Render sidebar navigation, server configuration, threshold controls, and system info."""
    with st.sidebar:
        render_html(
            """
            <div style="text-align: center; padding: 10px 0 16px 0;">
                <div style="font-size: 2.2rem; margin-bottom: 4px;">🏦</div>
                <div style="font-size: 1.3rem; font-weight: 800; letter-spacing: -0.02em; color: #f8fafc;">
                    Retain<span style="color: #6366f1;">IQ</span>
                </div>
                <div style="font-size: 0.78rem; color: #94a3b8;">Customer Retention AI Suite</div>
            </div>
            """
        )

        st.markdown("### 📌 Navigation")
        selected_view = st.radio(
            label="Select View",
            options=[
                "🔮 Single Customer Scoring",
                "📊 Batch Portfolio Scoring",
                "📈 Historical Insights & EDA",
                "⚙️ System Health & API Monitor",
            ],
            index=0,
            label_visibility="collapsed",
        )

        st.markdown("---")

        # API & Backend Configuration
        with st.expander("🔌 Backend API Connection", expanded=False):
            api_url = st.text_input("API Base URL", value=st.session_state.get("api_url", DEFAULT_API_URL))
            username = st.text_input("API Username", value=st.session_state.get("api_user", DEFAULT_API_USERNAME))
            password = st.text_input("API Password", value=st.session_state.get("api_pass", DEFAULT_API_PASSWORD), type="password")

            st.session_state["api_url"] = api_url
            st.session_state["api_user"] = username
            st.session_state["api_pass"] = password

            force_local = st.checkbox(
                "Use Standalone Local Engine",
                value=st.session_state.get("force_local", False),
                help="Bypasses HTTP API and evaluates predictions directly in-memory using local artifacts.",
            )
            st.session_state["force_local"] = force_local

            if st.button("🔄 Test Connection", use_container_width=True):
                api_client.base_url = api_url
                api_client.username = username
                api_client.password = password
                health = api_client.check_health()
                if health.get("online"):
                    st.success(f"Connected! Latency: {health['latency_ms']}ms")
                else:
                    st.error(f"Failed to reach API: {health.get('error', 'Unknown error')}")

        # Model Decision Threshold Adjuster
        with st.expander("⚖️ Decision Threshold", expanded=False):
            st.caption(
                "The LightGBM model was calibrated with an optimal F1 threshold of **0.23** during training."
            )
            custom_threshold = st.slider(
                "Classification Cutoff",
                min_value=0.05,
                max_value=0.95,
                value=st.session_state.get("custom_threshold", 0.23),
                step=0.01,
                help="Customers with predicted probability >= this threshold are flagged as Churn.",
            )
            st.session_state["custom_threshold"] = custom_threshold

            if st.button("Reset to Default (0.23)", use_container_width=True):
                st.session_state["custom_threshold"] = 0.23
                st.rerun()

        # Architecture & Model Info
        st.markdown("---")
        render_html(
            """
            <div style="font-size: 0.76rem; color: #64748b; line-height: 1.5;">
                <div><b>Model:</b> LightGBM Classifier</div>
                <div><b>Features:</b> 19 engineered features</div>
                <div><b>Caching:</b> Redis 8.4 (SHA256 hash)</div>
                <div><b>Metrics:</b> Prometheus + Grafana</div>
            </div>
            """
        )

        return {
            "selected_view": selected_view,
            "api_url": api_url,
            "username": username,
            "password": password,
            "force_local": force_local,
            "custom_threshold": custom_threshold,
        }
