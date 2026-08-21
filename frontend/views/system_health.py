"""System Health, API Diagnostics, Latency Benchmarking and Prometheus Metrics View."""

from typing import Any, Dict
import streamlit as st

from frontend.components.cards import render_kpi_card
from frontend.config import MODEL_PATH


def render_system_health_view(
    api_client: Any,
    api_url: str,
    username: str,
) -> None:
    """Render API diagnostics, latency tests, cache status, and Prometheus instrumentation."""
    st.markdown("## ⚙️ System Health, Architecture & API Diagnostics")
    st.caption("Inspect FastAPI microservice status, Redis caching behavior, Prometheus metrics, and endpoint contracts.")

    # Live Health Probe
    health = api_client.check_health()
    is_online = health.get("online", False)
    latency = health.get("latency_ms", 0.0)

    # Health KPIs
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        render_kpi_card("FastAPI Service", "ONLINE" if is_online else "OFFLINE", api_url, "#10B981" if is_online else "#EF4444", "🔌")
    with k2:
        render_kpi_card("Roundtrip Latency", f"{latency:.1f} ms", "Health probe response", "#6366F1", "⚡")
    with k3:
        render_kpi_card("Redis Cache", "ACTIVE" if is_online else "DEGRADED", "TTL: 3600s | SHA256", "#F59E0B", "💾")
    with k4:
        render_kpi_card("Model Engine", "LightGBM", f"Path: {MODEL_PATH.name}", "#38BDF8", "🧠")

    st.markdown("---")

    tab1, tab2, tab3, tab4 = st.tabs(["📡 Live Endpoint Tester", "📊 Prometheus Metrics", "🔐 API Integration Guide", "🧬 Model Architecture"])

    with tab1:
        st.markdown("#### 🧪 Interactive API Endpoint Probe")
        
        test_col1, test_col2 = st.columns(2)
        with test_col1:
            st.markdown("##### 1. `GET /health`")
            if st.button("Probe `/health`", use_container_width=True):
                h_res = api_client.check_health()
                st.json(h_res)

        with test_col2:
            st.markdown("##### 2. `POST /predict` (Sample Ping)")
            if st.button("Send Test Prediction Request", use_container_width=True):
                sample_payload = {
                    "gender": "Female",
                    "age": 42,
                    "salary": 100000.0,
                    "geography": "France",
                    "tenure": 3,
                    "balance": 120000.0,
                    "numproducts": 1,
                    "hascreditcard": True,
                    "isactive": True,
                }
                pred_res = api_client.predict(sample_payload, allow_fallback=True)
                st.json(pred_res)

    with tab2:
        st.markdown("#### 📈 Prometheus Metrics Scrape Preview")
        st.caption("The FastAPI backend exposes unauthenticated Prometheus metrics at `/metrics` for Prometheus scraping.")

        if st.button("Fetch `/metrics` Live Text"):
            success, metrics_text = api_client.get_metrics_text()
            if success:
                st.code(metrics_text[:2000] + ("\n... [truncated]" if len(metrics_text) > 2000 else ""), language="text")
            else:
                st.warning(f"Could not reach `/metrics`: {metrics_text}")
        else:
            st.info("Click 'Fetch `/metrics` Live Text' above to query live metrics from the running backend.")

        st.markdown(
            """
            **Configured Prometheus Metrics:**
            - `retainediq_http_requests_total`: Counter tracking HTTP request volume labeled by method, path, and HTTP status code.
            - `retainediq_http_request_duration_seconds`: Histogram tracking request latency distribution.
            - `http_requests_total`: Instrumentator default request counters.
            """
        )

    with tab3:
        st.markdown("#### 💻 REST API Integration Snippets")
        st.caption("Use these code snippets to integrate RetainIQ churn predictions into external banking applications.")

        st.markdown("##### Python (`requests`)")
        st.code(
            f"""import requests
from requests.auth import HTTPBasicAuth

url = "{api_url}/predict"
auth = HTTPBasicAuth("{username}", "YOUR_PASSWORD")

payload = {{
    "gender": "Female",
    "age": 42,
    "salary": 101348.88,
    "geography": "France",
    "tenure": 2,
    "balance": 119827.49,
    "numproducts": 1,
    "hascreditcard": True,
    "isactive": True
}}

response = requests.post(url, json=payload, auth=auth)
print(response.json())
# Output: {{"churn_probability": 0.1748, "churn_prediction": False, "threshold": 0.23, "cache_status": "cache_hit"}}
""",
            language="python",
        )

        st.markdown("##### cURL Command")
        st.code(
            f"""curl -X POST "{api_url}/predict" \\
  -u "{username}:change-me" \\
  -H "Content-Type: application/json" \\
  -d '{{
    "gender": "Female",
    "age": 42,
    "salary": 101348.88,
    "geography": "France",
    "tenure": 2,
    "balance": 119827.49,
    "numproducts": 1,
    "hascreditcard": true,
    "isactive": true
  }}'
""",
            language="bash",
        )

    with tab4:
        st.markdown("#### 🧬 Model Specs & Feature Engineering")
        st.markdown(
            """
            - **Algorithm:** LightGBM Binary Classifier (`objective="binary"`)
            - **Tuned Hyperparameters:** `RandomizedSearchCV` with Stratified K-Fold cross-validation
            - **Optimal Decision Threshold:** `0.23` (calibrated on validation set to maximize F1-Score)
            - **Engineered Features:**
              1. `balancesalaryratio` = $\\text{Balance} / \\max(\\text{Salary}, 1)$
              2. `tenurebyage` = $\\text{Tenure} / \\max(\\text{Age}, 1)$
              3. Categorical one-hot features (`gender`, `geography`, `hascreditcard`, `isactive`)
            - **Cache Strategy:** SHA-256 canonical JSON hash key stored in Redis with 3600s TTL.
            """
        )
