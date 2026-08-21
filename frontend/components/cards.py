"""Card components, KPI widgets, risk badges, and verdict display blocks."""

from typing import Any, Dict, List
import streamlit as st

from frontend.config import get_risk_tier
from frontend.utils.helpers import format_percent
from frontend.utils.styling import render_html


def render_kpi_card(
    title: str,
    value: str,
    subtitle: str = "",
    color: str = "#6366f1",
    icon: str = "📊",
) -> None:
    """Render a styled KPI metric card."""
    card_html = f"""
    <div class="kpi-card" style="border-top: 3px solid {color};">
        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
            <span class="kpi-label">{title}</span>
            <span style="font-size: 1.1rem;">{icon}</span>
        </div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-desc">{subtitle}</div>
    </div>
    """
    render_html(card_html)


def render_prediction_banner(
    prediction_result: Dict[str, Any],
    custom_threshold: float,
) -> None:
    """Render high-impact churn verdict banner with probability gauge and risk breakdown."""
    prob = prediction_result.get("churn_probability", 0.0)
    churn_flag = prob >= custom_threshold
    cache_status = prediction_result.get("cache_status", "cache_unavailable")
    latency_ms = prediction_result.get("latency_ms", 0.0)
    source = prediction_result.get("source", "FastAPI Service")

    risk_info = get_risk_tier(prob)
    css_class = "pred-churn" if churn_flag else "pred-retained"
    verdict_text = "HIGH CHURN RISK" if churn_flag else "LOW CHURN RISK (RETAINED)"
    verdict_icon = "⚠️" if churn_flag else "✅"
    verdict_color = "#ef4444" if churn_flag else "#10b981"

    # Cache status badge html
    if cache_status == "cache_hit":
        cache_badge = '<span class="badge-pill badge-cache-hit">⚡ Redis Cache Hit</span>'
    elif cache_status == "cache_miss":
        cache_badge = '<span class="badge-pill badge-cache-miss">💾 Redis Cache Miss (Stored)</span>'
    elif cache_status == "local_engine":
        cache_badge = '<span class="badge-pill badge-fallback">🧠 In-Memory ML Engine</span>'
    else:
        cache_badge = '<span class="badge-pill" style="background:rgba(100,116,139,0.2);color:#94a3b8;">⚙️ Uncached</span>'

    banner_html = f"""
    <div class="prediction-container {css_class}">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
            <div>
                <div style="font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.08em; color: {verdict_color}; font-weight: 700;">
                    Model Verdict &amp; Assessment
                </div>
                <div style="font-size: 1.6rem; font-weight: 800; color: #ffffff; margin-top: 2px;">
                    {verdict_icon} {verdict_text}
                </div>
            </div>
            <div style="display: flex; gap: 8px; align-items: center; flex-wrap: wrap;">
                {cache_badge}
                <span class="badge-pill" style="background: rgba(255,255,255,0.06); color: #cbd5e1; border: 1px solid rgba(255,255,255,0.1);">
                    ⏱️ {latency_ms:.1f}ms
                </span>
                <span class="badge-pill" style="background: rgba(255,255,255,0.06); color: #cbd5e1; border: 1px solid rgba(255,255,255,0.1);">
                    📡 {source}
                </span>
            </div>
        </div>

        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 16px; margin-top: 20px; padding-top: 16px; border-top: 1px solid rgba(255,255,255,0.1);">
            <div>
                <div style="font-size: 0.8rem; color: #94a3b8;">Churn Probability</div>
                <div style="font-size: 1.8rem; font-weight: 800; color: {risk_info['color']};">
                    {format_percent(prob)}
                </div>
            </div>
            <div>
                <div style="font-size: 0.8rem; color: #94a3b8;">Risk Classification</div>
                <div style="font-size: 1.2rem; font-weight: 700; color: #f8fafc; margin-top: 4px;">
                    {risk_info['icon']} {risk_info['tier']}
                </div>
            </div>
            <div>
                <div style="font-size: 0.8rem; color: #94a3b8;">Decision Threshold</div>
                <div style="font-size: 1.2rem; font-weight: 700; color: #f8fafc; margin-top: 4px;">
                    {custom_threshold:.2f} ({format_percent(custom_threshold)})
                </div>
            </div>
            <div>
                <div style="font-size: 0.8rem; color: #94a3b8;">Recommended Stance</div>
                <div style="font-size: 0.95rem; font-weight: 600; color: #e2e8f0; margin-top: 4px;">
                    {"Urgent Intervention" if churn_flag else "Routine Relationship Nurture"}
                </div>
            </div>
        </div>
    </div>
    """
    render_html(banner_html)


def render_risk_drivers_list(drivers: List[Dict[str, Any]]) -> None:
    """Render list of identified positive and negative risk factors."""
    st.markdown("#### 🔍 Key Risk Drivers &amp; Customer Signals")
    for driver in drivers:
        is_neg = driver["type"] == "negative"
        border_color = "#ef4444" if is_neg else "#10b981"
        badge_color = "rgba(239, 68, 68, 0.15)" if is_neg else "rgba(16, 185, 129, 0.15)"
        badge_text_color = "#f87171" if is_neg else "#34d399"
        icon = "🔴" if is_neg else "🟢"

        card_html = f"""
        <div style="background: rgba(30, 41, 59, 0.4); border-left: 4px solid {border_color}; border-radius: 0 10px 10px 0; padding: 12px 16px; margin-bottom: 10px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div style="font-weight: 600; font-size: 0.95rem; color: #f8fafc;">
                    {icon} {driver['factor']}
                </div>
                <span style="background: {badge_color}; color: {badge_text_color}; font-size: 0.75rem; font-weight: 700; padding: 2px 8px; border-radius: 9999px;">
                    {driver['impact']}
                </span>
            </div>
            <div style="font-size: 0.82rem; color: #94a3b8; margin-top: 4px;">
                {driver['detail']}
            </div>
        </div>
        """
        render_html(card_html)
