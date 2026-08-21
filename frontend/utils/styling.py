"""Custom CSS styling and visual theming for RetainIQ Streamlit application."""

import textwrap
import streamlit as st


def render_html(html_str: str) -> None:
    """Render HTML string safely without triggering Markdown indentation code-block parsing."""
    cleaned = textwrap.dedent(html_str).strip()
    if hasattr(st, "html"):
        st.html(cleaned)
    else:
        st.markdown(cleaned, unsafe_allow_html=True)


def apply_custom_styles() -> None:
    """Inject custom modern CSS into the Streamlit application."""
    custom_css = """
    <style>
    /* Global Fonts & Spacing */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }

    /* Top Header Gradient Banner */
    .hero-banner {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #311042 100%);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 24px 28px;
        margin-bottom: 24px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3), 0 8px 10px -6px rgba(0, 0, 0, 0.2);
        color: #ffffff;
    }

    .hero-title {
        font-size: 1.85rem;
        font-weight: 800;
        letter-spacing: -0.025em;
        background: linear-gradient(to right, #60a5fa, #a78bfa, #f472b6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 6px;
    }

    .hero-subtitle {
        color: #94a3b8;
        font-size: 0.95rem;
        margin-bottom: 0px;
    }

    /* Metric & KPI Cards */
    .kpi-card {
        background: rgba(30, 41, 59, 0.7);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 18px 20px;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }

    .kpi-card:hover {
        transform: translateY(-2px);
        border-color: rgba(99, 102, 241, 0.4);
    }

    .kpi-label {
        font-size: 0.82rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #94a3b8;
        margin-bottom: 6px;
    }

    .kpi-value {
        font-size: 1.75rem;
        font-weight: 700;
        color: #f8fafc;
        line-height: 1.2;
    }

    .kpi-desc {
        font-size: 0.78rem;
        color: #64748b;
        margin-top: 4px;
    }

    /* Status Badges */
    .badge-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 600;
        line-height: 1;
    }

    .badge-online {
        background: rgba(16, 185, 129, 0.15);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }

    .badge-offline {
        background: rgba(239, 68, 68, 0.15);
        color: #f87171;
        border: 1px solid rgba(239, 68, 68, 0.3);
    }

    .badge-fallback {
        background: rgba(245, 158, 11, 0.15);
        color: #fbbf24;
        border: 1px solid rgba(245, 158, 11, 0.3);
    }

    .badge-cache-hit {
        background: rgba(59, 130, 246, 0.15);
        color: #60a5fa;
        border: 1px solid rgba(59, 130, 246, 0.3);
    }

    .badge-cache-miss {
        background: rgba(147, 51, 234, 0.15);
        color: #c084fc;
        border: 1px solid rgba(147, 51, 234, 0.3);
    }

    /* Prediction Result Card */
    .prediction-container {
        border-radius: 16px;
        padding: 24px;
        margin: 16px 0;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }

    .pred-churn {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.15) 0%, rgba(185, 28, 28, 0.08) 100%);
        border-color: rgba(239, 68, 68, 0.4);
    }

    .pred-retained {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(5, 150, 105, 0.08) 100%);
        border-color: rgba(16, 185, 129, 0.4);
    }

    .recommendation-card {
        background: rgba(30, 41, 59, 0.5);
        border-left: 4px solid #6366f1;
        border-radius: 0 10px 10px 0;
        padding: 14px 18px;
        margin-bottom: 12px;
    }

    /* Custom scrollbars */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }
    ::-webkit-scrollbar-track {
        background: transparent;
    }
    ::-webkit-scrollbar-thumb {
        background: rgba(148, 163, 184, 0.3);
        border-radius: 3px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(148, 163, 184, 0.5);
    }
    </style>
    """
    render_html(custom_css)
