"""Main Application Entry Point for RetainIQ Streamlit Dashboard."""

import streamlit as st

from frontend.api_client import RetainIQApiClient
from frontend.components.header import render_header
from frontend.components.sidebar import render_sidebar
from frontend.config import (
    DEFAULT_API_PASSWORD,
    DEFAULT_API_URL,
    DEFAULT_API_USERNAME,
)
from frontend.utils.styling import apply_custom_styles, render_html
from frontend.views.batch_prediction import render_batch_prediction_view
from frontend.views.customer_insights import render_customer_insights_view
from frontend.views.single_prediction import render_single_prediction_view
from frontend.views.system_health import render_system_health_view


def main() -> None:
    """Initialize and run the RetainIQ Streamlit application."""
    st.set_page_config(
        page_title="RetainIQ | Banking Churn AI",
        page_icon="🏦",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Apply Custom CSS styling
    apply_custom_styles()

    # Session State Initialization
    if "api_url" not in st.session_state:
        st.session_state["api_url"] = DEFAULT_API_URL
    if "api_user" not in st.session_state:
        st.session_state["api_user"] = DEFAULT_API_USERNAME
    if "api_pass" not in st.session_state:
        st.session_state["api_pass"] = DEFAULT_API_PASSWORD
    if "custom_threshold" not in st.session_state:
        st.session_state["custom_threshold"] = 0.23
    if "force_local" not in st.session_state:
        st.session_state["force_local"] = False

    # Instantiate API Client
    api_client = RetainIQApiClient(
        base_url=st.session_state["api_url"],
        username=st.session_state["api_user"],
        password=st.session_state["api_pass"],
        timeout=10.0,
    )

    # Health check for header status badge
    health_status = api_client.check_health()

    # Render Sidebar Controls & Navigation
    sidebar_state = render_sidebar(api_client)
    selected_view = sidebar_state["selected_view"]
    custom_threshold = sidebar_state["custom_threshold"]
    force_local = sidebar_state["force_local"]

    # Render Main Top Header
    render_header(health_status, standalone_mode=force_local)

    # View Router
    if selected_view == "🔮 Single Customer Scoring":
        render_single_prediction_view(
            api_client=api_client,
            custom_threshold=custom_threshold,
            force_local=force_local,
        )
    elif selected_view == "📊 Batch Portfolio Scoring":
        render_batch_prediction_view(
            api_client=api_client,
            custom_threshold=custom_threshold,
            force_local=force_local,
        )
    elif selected_view == "📈 Historical Insights & EDA":
        render_customer_insights_view()
    elif selected_view == "⚙️ System Health & API Monitor":
        render_system_health_view(
            api_client=api_client,
            api_url=sidebar_state["api_url"],
            username=sidebar_state["username"],
        )

    # Footer
    st.markdown("---")
    render_html(
        """
        <div style="text-align: center; font-size: 0.78rem; color: #64748b; padding: 12px 0;">
            <b>RetainIQ Enterprise</b> &bull; Banking Customer Attrition Analytics &amp; Decision Intelligence &bull; Powered by LightGBM &amp; FastAPI
        </div>
        """
    )


if __name__ == "__main__":
    main()
