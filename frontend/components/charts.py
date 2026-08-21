"""Visualizations, gauges, sensitivity analysis, and distribution charts."""

from typing import Any, Dict, List
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

from frontend.config import get_risk_tier
from frontend.utils.helpers import format_percent


def render_gauge_chart(probability: float, threshold: float) -> None:
    """Render a modern semi-circular gauge chart showing the predicted probability."""
    fig, ax = plt.subplots(figsize=(6, 3.2), subplot_kw={"projection": "polar"})
    fig.patch.set_facecolor("none")
    ax.set_facecolor("none")

    # Polar range for semi-circle gauge (pi to 0)
    theta = np.linspace(np.pi, 0, 100)

    # Background color arcs
    # Low Risk (0 to 0.20): Green
    t_low = np.linspace(np.pi, np.pi * 0.80, 50)
    ax.plot(t_low, [1.0] * len(t_low), color="#10B981", lw=14, solid_capstyle="round")

    # Moderate Risk (0.20 to 0.35): Amber
    t_med = np.linspace(np.pi * 0.80, np.pi * 0.65, 50)
    ax.plot(t_med, [1.0] * len(t_med), color="#F59E0B", lw=14)

    # High Risk (0.35 to 0.60): Orange
    t_high = np.linspace(np.pi * 0.65, np.pi * 0.40, 50)
    ax.plot(t_high, [1.0] * len(t_high), color="#F97316", lw=14)

    # Critical Risk (0.60 to 1.0): Crimson
    t_crit = np.linspace(np.pi * 0.40, 0, 50)
    ax.plot(t_crit, [1.0] * len(t_crit), color="#EF4444", lw=14, solid_capstyle="round")

    # Needle calculation
    clamped_prob = min(max(probability, 0.0), 1.0)
    needle_angle = np.pi - (clamped_prob * np.pi)

    # Draw Needle
    ax.annotate(
        "",
        xy=(needle_angle, 0.95),
        xytext=(0, 0),
        arrowprops=dict(arrowstyle="->", color="#FFFFFF", lw=3.0, mutation_scale=16),
    )

    # Threshold indicator tick
    thresh_angle = np.pi - (threshold * np.pi)
    ax.plot([thresh_angle, thresh_angle], [0.85, 1.15], color="#F43F5E", lw=2.5, linestyle="--")

    ax.set_ylim(0, 1.25)
    ax.set_yticks([])
    ax.set_xticks([np.pi, np.pi * 0.75, np.pi * 0.5, np.pi * 0.25, 0])
    ax.set_xticklabels(["0%", "25%", "50%", "75%", "100%"], color="#94A3B8", fontsize=9, fontweight="bold")
    ax.spines["polar"].set_visible(False)
    ax.grid(False)

    risk_info = get_risk_tier(probability)
    ax.text(
        0,
        -0.25,
        f"{format_percent(probability)}\n{risk_info['tier']}",
        horizontalalignment="center",
        verticalalignment="center",
        fontsize=13,
        fontweight="bold",
        color=risk_info["color"],
    )

    st.pyplot(fig, use_container_width=True)
    plt.close(fig)


def render_whatif_sensitivity_chart(
    base_payload: Dict[str, Any],
    api_client: Any,
    custom_threshold: float,
) -> None:
    """Generate sensitivity curves showing how altering age and products affects churn probability."""
    st.markdown("#### 📈 What-If Sensitivity Curves")
    st.caption("Inspect how customer churn risk shifts across varying ages and product configurations.")

    test_ages = list(range(20, 75, 4))
    prod_options = [1, 2, 3, 4]
    curve_data: List[Dict[str, Any]] = []

    for num_p in prod_options:
        for age in test_ages:
            sim_payload = dict(base_payload)
            sim_payload["age"] = age
            sim_payload["numproducts"] = num_p
            try:
                res = api_client.predict(sim_payload, allow_fallback=True)
                prob = res.get("churn_probability", 0.0)
            except Exception:
                prob = 0.20
            curve_data.append({"Age": age, "Products": f"{num_p} Product{'s' if num_p > 1 else ''}", "Churn Probability": prob})

    df_curve = pd.DataFrame(curve_data)

    fig, ax = plt.subplots(figsize=(8, 4))
    fig.patch.set_facecolor("#0F172A")
    ax.set_facecolor("#1E293B")

    colors = ["#EF4444", "#10B981", "#F59E0B", "#8B5CF6"]
    for idx, num_p in enumerate(prod_options):
        subset = df_curve[df_curve["Products"] == f"{num_p} Product{'s' if num_p > 1 else ''}"]
        ax.plot(
            subset["Age"],
            subset["Churn Probability"],
            label=f"{num_p} Product{'s' if num_p > 1 else ''}",
            color=colors[idx % len(colors)],
            linewidth=2.2,
            marker="o",
            markersize=4,
        )

    # Current customer reference point
    curr_age = base_payload.get("age", 40)
    curr_res = api_client.predict(base_payload, allow_fallback=True)
    curr_prob = curr_res.get("churn_probability", 0.0)
    ax.scatter(
        [curr_age],
        [curr_prob],
        color="#38BDF8",
        s=120,
        zorder=5,
        edgecolors="#FFFFFF",
        linewidth=2,
        label="Current Customer",
    )

    # Decision threshold line
    ax.axhline(
        y=custom_threshold,
        color="#F43F5E",
        linestyle="--",
        linewidth=1.8,
        label=f"Decision Threshold ({custom_threshold:.2f})",
    )

    ax.set_title("Churn Risk vs. Age by Product Holdings", color="#F8FAFC", fontsize=11, fontweight="bold", pad=12)
    ax.set_xlabel("Customer Age (Years)", color="#94A3B8", fontsize=9)
    ax.set_ylabel("Predicted Churn Probability", color="#94A3B8", fontsize=9)
    ax.tick_params(colors="#94A3B8")
    ax.set_ylim(0, 1.0)
    ax.grid(True, linestyle=":", alpha=0.3, color="#64748B")
    ax.legend(facecolor="#0F172A", edgecolor="#334155", labelcolor="#F8FAFC", fontsize=8, loc="upper left")

    st.pyplot(fig, use_container_width=True)
    plt.close(fig)


def render_batch_analytics_charts(scored_df: pd.DataFrame, custom_threshold: float) -> None:
    """Render batch distribution charts and risk breakdowns."""
    col1, col2 = st.columns(2)

    with col1:
        # Churn Probability Distribution Histogram
        fig, ax = plt.subplots(figsize=(6, 3.8))
        fig.patch.set_facecolor("#0F172A")
        ax.set_facecolor("#1E293B")

        n, bins, patches = ax.hist(
            scored_df["churn_probability"],
            bins=15,
            color="#6366F1",
            edgecolor="#0F172A",
            alpha=0.85,
        )

        for patch, left_side in zip(patches, bins[:-1]):
            if left_side >= custom_threshold:
                patch.set_facecolor("#EF4444")
            else:
                patch.set_facecolor("#10B981")

        ax.axvline(
            custom_threshold,
            color="#F8FAFC",
            linestyle="--",
            linewidth=2,
            label=f"Threshold ({custom_threshold:.2f})",
        )
        ax.set_title("Predicted Churn Probability Distribution", color="#F8FAFC", fontsize=10, fontweight="bold")
        ax.set_xlabel("Churn Probability", color="#94A3B8", fontsize=8)
        ax.set_ylabel("Number of Customers", color="#94A3B8", fontsize=8)
        ax.tick_params(colors="#94A3B8")
        ax.grid(True, linestyle=":", alpha=0.3, color="#64748B")
        ax.legend(facecolor="#0F172A", edgecolor="#334155", labelcolor="#F8FAFC", fontsize=8)
        st.pyplot(fig, use_container_width=True)
        plt.close(fig)

    with col2:
        # Risk by Geography Bar Chart
        if "geography" in scored_df.columns:
            geo_summary = (
                scored_df.groupby("geography")["churn_flag"]
                .mean()
                .reset_index()
                .rename(columns={"churn_flag": "churn_rate"})
            )

            fig, ax = plt.subplots(figsize=(6, 3.8))
            fig.patch.set_facecolor("#0F172A")
            ax.set_facecolor("#1E293B")

            bars = ax.bar(
                geo_summary["geography"],
                geo_summary["churn_rate"] * 100,
                color="#38BDF8",
                edgecolor="#0F172A",
                width=0.55,
            )

            for bar in bars:
                height = bar.get_height()
                ax.annotate(
                    f"{height:.1f}%",
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha="center",
                    va="bottom",
                    color="#F8FAFC",
                    fontsize=8,
                    fontweight="bold",
                )

            ax.set_title("Churn Rate by Geography (%)", color="#F8FAFC", fontsize=10, fontweight="bold")
            ax.set_ylabel("Churn Rate (%)", color="#94A3B8", fontsize=8)
            ax.tick_params(colors="#94A3B8")
            ax.set_ylim(0, max(geo_summary["churn_rate"].max() * 120, 20))
            ax.grid(True, axis="y", linestyle=":", alpha=0.3, color="#64748B")
            st.pyplot(fig, use_container_width=True)
            plt.close(fig)


def render_historical_eda_charts(df: pd.DataFrame) -> None:
    """Render comprehensive historical exploratory data analysis charts."""
    tab1, tab2, tab3 = st.tabs(["🌍 Geography & Demographics", "💳 Financials & Products", "⚡ Behavioral Engagement"])

    with tab1:
        c1, c2 = st.columns(2)
        with c1:
            geo_churn = df.groupby("geography")["churned"].mean().reset_index()
            fig, ax = plt.subplots(figsize=(6, 3.8))
            fig.patch.set_facecolor("#0F172A")
            ax.set_facecolor("#1E293B")
            bars = ax.bar(geo_churn["geography"], geo_churn["churned"] * 100, color="#818CF8", width=0.5)
            for bar in bars:
                ax.annotate(
                    f"{bar.get_height():.1f}%",
                    xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha="center",
                    color="#F8FAFC",
                    fontweight="bold",
                    fontsize=8,
                )
            ax.set_title("Historical Churn Rate by Geography (%)", color="#F8FAFC", fontsize=10, fontweight="bold")
            ax.set_ylabel("Churn %", color="#94A3B8", fontsize=8)
            ax.tick_params(colors="#94A3B8")
            ax.grid(True, axis="y", linestyle=":", alpha=0.3, color="#64748B")
            st.pyplot(fig, use_container_width=True)
            plt.close(fig)

        with c2:
            gender_churn = df.groupby("gender")["churned"].mean().reset_index()
            fig, ax = plt.subplots(figsize=(6, 3.8))
            fig.patch.set_facecolor("#0F172A")
            ax.set_facecolor("#1E293B")
            bars = ax.bar(gender_churn["gender"], gender_churn["churned"] * 100, color=["#F472B6", "#60A5FA"], width=0.45)
            for bar in bars:
                ax.annotate(
                    f"{bar.get_height():.1f}%",
                    xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha="center",
                    color="#F8FAFC",
                    fontweight="bold",
                    fontsize=8,
                )
            ax.set_title("Historical Churn Rate by Gender (%)", color="#F8FAFC", fontsize=10, fontweight="bold")
            ax.set_ylabel("Churn %", color="#94A3B8", fontsize=8)
            ax.tick_params(colors="#94A3B8")
            ax.grid(True, axis="y", linestyle=":", alpha=0.3, color="#64748B")
            st.pyplot(fig, use_container_width=True)
            plt.close(fig)

    with tab2:
        c1, c2 = st.columns(2)
        with c1:
            prod_churn = df.groupby("numproducts")["churned"].mean().reset_index()
            fig, ax = plt.subplots(figsize=(6, 3.8))
            fig.patch.set_facecolor("#0F172A")
            ax.set_facecolor("#1E293B")
            bars = ax.bar(prod_churn["numproducts"].astype(str), prod_churn["churned"] * 100, color="#34D399", width=0.5)
            for bar in bars:
                ax.annotate(
                    f"{bar.get_height():.1f}%",
                    xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha="center",
                    color="#F8FAFC",
                    fontweight="bold",
                    fontsize=8,
                )
            ax.set_title("Churn Rate by Number of Products Held (%)", color="#F8FAFC", fontsize=10, fontweight="bold")
            ax.set_xlabel("Number of Products", color="#94A3B8", fontsize=8)
            ax.set_ylabel("Churn %", color="#94A3B8", fontsize=8)
            ax.tick_params(colors="#94A3B8")
            ax.grid(True, axis="y", linestyle=":", alpha=0.3, color="#64748B")
            st.pyplot(fig, use_container_width=True)
            plt.close(fig)

        with c2:
            fig, ax = plt.subplots(figsize=(6, 3.8))
            fig.patch.set_facecolor("#0F172A")
            ax.set_facecolor("#1E293B")
            retained_balance = df[df["churned"] == 0]["balance"]
            churned_balance = df[df["churned"] == 1]["balance"]
            ax.hist(retained_balance, bins=20, alpha=0.6, label="Retained", color="#10B981", density=True)
            ax.hist(churned_balance, bins=20, alpha=0.6, label="Churned", color="#EF4444", density=True)
            ax.set_title("Balance Distribution: Churned vs Retained", color="#F8FAFC", fontsize=10, fontweight="bold")
            ax.set_xlabel("Account Balance ($)", color="#94A3B8", fontsize=8)
            ax.tick_params(colors="#94A3B8")
            ax.grid(True, linestyle=":", alpha=0.3, color="#64748B")
            ax.legend(facecolor="#0F172A", edgecolor="#334155", labelcolor="#F8FAFC", fontsize=8)
            st.pyplot(fig, use_container_width=True)
            plt.close(fig)

    with tab3:
        c1, c2 = st.columns(2)
        with c1:
            active_churn = df.groupby("isactive")["churned"].mean().reset_index()
            active_churn["isactive_str"] = active_churn["isactive"].map({True: "Active Member", False: "Inactive Member"})
            fig, ax = plt.subplots(figsize=(6, 3.8))
            fig.patch.set_facecolor("#0F172A")
            ax.set_facecolor("#1E293B")
            bars = ax.bar(active_churn["isactive_str"], active_churn["churned"] * 100, color=["#EF4444", "#10B981"], width=0.45)
            for bar in bars:
                ax.annotate(
                    f"{bar.get_height():.1f}%",
                    xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha="center",
                    color="#F8FAFC",
                    fontweight="bold",
                    fontsize=8,
                )
            ax.set_title("Churn Rate by Member Activity Status (%)", color="#F8FAFC", fontsize=10, fontweight="bold")
            ax.set_ylabel("Churn %", color="#94A3B8", fontsize=8)
            ax.tick_params(colors="#94A3B8")
            ax.grid(True, axis="y", linestyle=":", alpha=0.3, color="#64748B")
            st.pyplot(fig, use_container_width=True)
            plt.close(fig)

        with c2:
            fig, ax = plt.subplots(figsize=(6, 3.8))
            fig.patch.set_facecolor("#0F172A")
            ax.set_facecolor("#1E293B")
            retained_age = df[df["churned"] == 0]["age"]
            churned_age = df[df["churned"] == 1]["age"]
            ax.hist(retained_age, bins=20, alpha=0.6, label="Retained", color="#38BDF8", density=True)
            ax.hist(churned_age, bins=20, alpha=0.6, label="Churned", color="#F97316", density=True)
            ax.set_title("Age Distribution: Churned vs Retained", color="#F8FAFC", fontsize=10, fontweight="bold")
            ax.set_xlabel("Customer Age (Years)", color="#94A3B8", fontsize=8)
            ax.tick_params(colors="#94A3B8")
            ax.grid(True, linestyle=":", alpha=0.3, color="#64748B")
            ax.legend(facecolor="#0F172A", edgecolor="#334155", labelcolor="#F8FAFC", fontsize=8)
            st.pyplot(fig, use_container_width=True)
            plt.close(fig)
