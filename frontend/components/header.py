"""Header and top banner component for the RetainIQ Dashboard."""

from typing import Any, Dict
import streamlit as st

from frontend.utils.styling import render_html


def render_header(health_status: Dict[str, Any], standalone_mode: bool = False) -> None:
    """Render the application header with status indicator and live system health badge."""
    col1, col2 = st.columns([3, 1.2])

    with col1:
        render_html(
            """
            <div class="hero-banner">
                <div class="hero-title">RetainIQ 🏦 Churn Intelligence & Decision Engine</div>
                <p class="hero-subtitle">
                    Enterprise Banking Customer Churn Analytics, Real-Time Risk Scoring & Prescriptive Retention AI
                </p>
            </div>
            """
        )

    with col2:
        if standalone_mode:
            status_html = """
            <div style="text-align: right; padding-top: 10px;">
                <span class="badge-pill badge-fallback">
                    <span>⚡</span> <b>Engine: Local Fallback</b>
                </span>
                <div style="font-size: 0.75rem; color: #94a3b8; margin-top: 6px;">Direct In-Memory Inference</div>
            </div>
            """
        elif health_status.get("online"):
            latency = health_status.get("latency_ms", 0.0)
            status_html = f"""
            <div style="text-align: right; padding-top: 10px;">
                <span class="badge-pill badge-online">
                    <span style="display:inline-block; width:8px; height:8px; border-radius:50%; background:#10B981;"></span>
                    <b>API Live ({latency:.1f}ms)</b>
                </span>
                <div style="font-size: 0.75rem; color: #94a3b8; margin-top: 6px;">FastAPI + Redis Active</div>
            </div>
            """
        else:
            status_html = """
            <div style="text-align: right; padding-top: 10px;">
                <span class="badge-pill badge-offline">
                    <span style="display:inline-block; width:8px; height:8px; border-radius:50%; background:#EF4444;"></span>
                    <b>API Disconnected</b>
                </span>
                <div style="font-size: 0.75rem; color: #94a3b8; margin-top: 6px;">Using In-Memory Fallback</div>
            </div>
            """
        render_html(status_html)
