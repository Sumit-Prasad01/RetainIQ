# RetainIQ 🏦 | Banking Customer Churn Analytics & Predictive AI Engine

[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.40+-FF4B4B.svg?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![LightGBM](https://img.shields.io/badge/LightGBM-4.0+-brightgreen.svg)](https://lightgbm.readthedocs.io/)
[![Redis](https://img.shields.io/badge/Redis-8.0+-DC382D.svg?logo=redis&logoColor=white)](https://redis.io/)
[![Prometheus](https://img.shields.io/badge/Prometheus-Monitoring-E6522C.svg?logo=prometheus&logoColor=white)](https://prometheus.io/)
[![Grafana](https://img.shields.io/badge/Grafana-Dashboards-F46800.svg?logo=grafana&logoColor=white)](https://grafana.com/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg?logo=docker&logoColor=white)](https://www.docker.com/)

**RetainIQ** is an enterprise-grade, end-to-end Machine Learning and Decision Intelligence platform designed to identify, analyze, and proactively prevent customer churn in commercial banking portfolios. 

Combining high-performance **LightGBM** gradient boosted trees, **FastAPI** microservices with **Redis** SHA-256 caching, **Prometheus/Grafana** operational telemetry, and a modular **Streamlit** dashboard, RetainIQ empowers banking relationship managers and risk officers to turn predictive signals into prescriptive retention playbooks.

---

## 🏛️ System Architecture Diagrams

### 1. End-to-End System & ML Pipeline Architecture

```mermaid
flowchart TD
    subgraph Data_Layer ["Data & Storage Layer"]
        A1[("Raw Customer Data\n(Excel / Sheets)")] --> A2["Data Cleaning & Ingestion"]
        A2 --> A3[("PostgreSQL Database\n(Demographic, Account, Location)")]
        A3 --> A4["ETL & Feature Pipeline\n(balancesalaryratio, tenurebyage)"]
        A4 --> A5["Train / Validation / Test Splits\n(train_bundle.pkl)"]
    end

    subgraph ML_Layer ["Model Training & Experimentation"]
        A5 --> B1["Hyperparameter Tuning\n(RandomizedSearchCV + Stratified K-Fold)"]
        B1 --> B2["Threshold Optimization\n(Optimal F1 Cutoff: 0.23)"]
        B2 --> B3[("MLflow Tracking & Registry\n(Params, Metrics, Artifacts)")]
        B2 --> B4["Model Artifact Packaging\n(lgbm_model.pkl)"]
    end

    subgraph Serving_Layer ["Serving & Infrastructure"]
        B4 --> C1["FastAPI Microservice\n(:8000/predict)"]
        C1 <--> C2[("Redis Caching\n(SHA256 Canonical JSON)")]
        C1 --> C3["Prometheus Telemetry\n(:8000/metrics)"]
        C3 --> C4["Grafana Observability Dashboard\n(:3000)"]
    end

    subgraph Frontend_Layer ["Presentation & Decision Suite"]
        C1 <--> D1["Streamlit Modular Frontend\n(:8501)"]
        D1 --> D2["🔮 Single Customer Scoring & What-If Simulator"]
        D1 --> D3["📊 Batch Portfolio Scoring & Export"]
        D1 --> D4["📈 Historical EDA & Insights"]
        D1 --> D5["⚙️ System Health & API Diagnostics"]
    end

    style Serving_Layer fill:#1e1b4b,stroke:#6366f1,stroke-width:2px,color:#fff
    style Frontend_Layer fill:#0f172a,stroke:#38bdf8,stroke-width:2px,color:#fff
    style ML_Layer fill:#14532d,stroke:#22c55e,stroke-width:2px,color:#fff
    style Data_Layer fill:#3b0764,stroke:#a855f7,stroke-width:2px,color:#fff
```

---

### 2. Real-Time Inference & Caching Workflow

```mermaid
sequenceDiagram
    autonumber
    actor User as Relationship Manager
    participant UI as Streamlit Frontend (Port 8501)
    participant API as FastAPI Gateway (Port 8000)
    participant Auth as HTTP Basic Auth Guard
    participant Cache as Redis Cache (Port 6379)
    participant Engine as ChurnPredictor Engine (LightGBM)

    User->>UI: Inputs Customer Profile / Selects Preset
    UI->>API: POST /predict (JSON Payload + Basic Auth)
    API->>Auth: Verify API credentials (admin / change-me)
    Auth-->>API: Authorized
    API->>API: Generate SHA256 Key from Canonical JSON
    API->>Cache: GET churn:prediction:<hash>
    
    alt Cache Hit
        Cache-->>API: Return Cached Result (churn_probability, threshold)
        API-->>UI: Response (cache_status = "cache_hit")
    else Cache Miss / Degraded
        API->>Engine: Run Preprocessing & Feature Engineering
        Engine->>Engine: Compute derived features (balancesalaryratio, tenurebyage)
        Engine->>Engine: One-Hot Encode Categoricals (19 Model Features)
        Engine->>Engine: Model.predict_proba() >= 0.23 Threshold
        Engine-->>API: Prediction Result
        API->>Cache: SETEX churn:prediction:<hash> 3600s
        API-->>UI: Response (cache_status = "cache_miss")
    end

    UI->>UI: Render Verdict Banner, Radial Gauge & Risk Drivers
    UI->>UI: Generate Prescriptive AI Retention Action Plan
    UI-->>User: Visual Decision Dashboard & What-If Simulator
```

---

### 3. Modular Codebase & Component Hierarchy

```mermaid
graph LR
    subgraph App_Root ["Root Orchestrator"]
        APP["app.py\n(Dual-Threaded Backend + Frontend Runner)"]
    end

    subgraph Backend_Modules ["backend/"]
        B_MAIN["main.py\n(FastAPI App + Prometheus Exposer)"]
        B_ROUTES["api/routes/\n(health.py, predictions.py)"]
        B_SCHEMAS["api/schemas/\n(prediction.py)"]
        B_SERVICES["services/\n(prediction.py - ChurnPredictor)"]
        B_CACHE["cache/\n(redis_cache.py)"]
        B_CORE["core/\n(auth.py - BasicAuth Guard)"]
        B_MW["middlewares/\n(request_metrics.py)"]
    end

    subgraph Frontend_Modules ["frontend/"]
        F_APP["app.py\n(Streamlit Page Router)"]
        F_CONFIG["config.py\n(Endpoints, Presets, Risk Tiers)"]
        F_CLIENT["api_client.py\n(API Client + Local Fallback)"]
        F_COMP["components/\n(header, sidebar, cards, forms, charts)"]
        F_VIEWS["views/\n(single, batch, insights, system_health)"]
        F_UTILS["utils/\n(styling, helpers, retention)"]
    end

    APP -->|Thread 1: Uvicorn| B_MAIN
    APP -->|Thread 2: Streamlit| F_APP
    B_MAIN --> B_ROUTES --> B_SERVICES
    B_ROUTES --> B_CACHE
    B_ROUTES --> B_CORE
    F_APP --> F_VIEWS
    F_VIEWS --> F_COMP
    F_VIEWS --> F_CLIENT
    F_VIEWS --> F_UTILS
```

---

## 🌟 Key Capabilities

### 1. 🔮 Single Customer Scoring & What-If Simulator
- **Instant Risk Assessment**: Computes attrition probability, classification verdict, and financial deposit exposure at risk.
- **Radial Probability Gauge**: Color-coded risk meter with visual decision threshold cutoffs.
- **Root-Cause Risk Drivers**: Identifies top contributors (e.g., account inactivity, single-product vulnerability, senior demographic bands, regional market baselines).
- **Prescriptive AI Retention Action Plan**: Generates targeted outreach strategies, designated communication channels, and expected churn reduction percentages.
- **Dynamic What-If Sensitivity Curves**: Interactive real-time curves showing how varying age, tenure, and product holdings alters retention likelihood.

### 2. 📊 Batch Portfolio Risk Analytics & Cohort Scoring
- **Bulk CSV Upload & Processing**: Score entire customer portfolios in seconds with live progress tracking.
- **Built-In Sample Data**: One-click demo loader with 50 real banking records and downloadable CSV templates.
- **Portfolio Summary KPIs**: Evaluated accounts, aggregate churn rate, total deposit capital at risk, and average attrition probability.
- **Filterable Explorer & CSV Export**: Segment by risk tier (*Critical, High, Moderate, Low*) and export enriched datasets with model probabilities.

### 3. 📈 Historical Portfolio Insights & Exploratory Data Analysis
- Interactive analytics across **10,000 historical commercial banking accounts**.
- Multi-dimensional breakdowns across **Geography** (*Germany, France, Spain, UK, Canada, USA*), **Gender**, **Age Demographics**, and **Product Breadth**.
- Strategic banking insights (*e.g., the "2-Product" sweet spot with <8% churn vs. >80% for 3+ products*).

### 4. ⚙️ Production-Ready Backend & Observability
- **FastAPI Microservice**: High-throughput REST API with Pydantic validation.
- **Redis Caching Layer**: Canonical JSON SHA-256 keying with automatic graceful degradation if Redis is offline.
- **Prometheus & Grafana**: Built-in operational monitoring tracking request counts, latencies, and status codes.
- **Standalone Local Fallback**: The frontend automatically switches to in-memory evaluation if the backend is unreachable.

---

## 🔬 Machine Learning Model Specifications

| Parameter | Specification |
| :--- | :--- |
| **Model Algorithm** | `LightGBMClassifier` (Gradient Boosted Decision Trees) |
| **Objective** | `binary` (Binary Cross-Entropy Loss) |
| **Optimization Strategy** | `RandomizedSearchCV` with 5-Fold Stratified Cross-Validation |
| **Optimized Decision Threshold** | **`0.23`** *(Calibrated on validation set to maximize F1-score on imbalanced churn classes)* |
| **Total Features** | **19 Features** (7 numerical + 12 one-hot encoded categorical) |
| **Engineered Features** | `balancesalaryratio` = $\frac{\text{Balance}}{\max(\text{Salary}, 1)}$, `tenurebyage` = $\frac{\text{Tenure}}{\max(\text{Age}, 1)}$ |
| **Artifact Path** | `artifacts/models/lgbm_model.pkl` |
| **Experiment Tracking** | MLflow (`mlruns/`, `mlflow.db`) |

---

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.11+ or 3.12+
- (Optional) Docker and Docker Compose for containerized stack

### 1. Clone & Environment Setup
```bash
# Clone the repository
git clone https://github.com/Sumit-Prasad01/RetainIQ.git
cd RetainIQ

# Create and activate virtual environment
python -m venv .venv
# Windows:
.\.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Create a `.env` file in the project root:
```env
API_USERNAME=admin
API_PASSWORD=change-me
REDIS_URL=redis://localhost:6379/0
PREDICTION_CACHE_TTL_SECONDS=3600
MODEL_PATH=artifacts/models/lgbm_model.pkl
```

### 3. Launch Application

#### Option A: Unified Launcher (Recommended)
Runs both the **FastAPI backend** (Port 8000) and **Streamlit frontend** (Port 8501) concurrently in a single command via [`app.py`](file:///C:/Users/sumit/OneDrive/Desktop/Code_PlayGround/End-To-End-ML-Projects/RetainIQ-Banking_Customer_Churn_Analytics-Predictive-Modelling/app.py):
```bash
python app.py
```

#### Option B: Launch Services Separately
```bash
# Terminal 1: Start FastAPI Backend
uvicorn backend.main:app --host 127.0.0.1 --port 8000

# Terminal 2: Start Streamlit Frontend
streamlit run frontend/app.py
```

#### Option C: Full Containerized Stack (Docker Compose)
Spawns FastAPI, Redis, PostgreSQL, Prometheus, and Grafana:
```bash
docker-compose up --build
```

---

## 📡 REST API Reference

The backend exposes authenticated REST endpoints. Default Basic Auth credentials: `admin` / `change-me`.

### 1. Health Probe
```http
GET /health
```
**Response:**
```json
{
  "status": "ok"
}
```

### 2. Predict Customer Churn
```http
POST /predict
Authorization: Basic YWRtaW46Y2hhbmdlLW1l
Content-Type: application/json
```

**Request Payload:**
```json
{
  "gender": "Female",
  "age": 42,
  "salary": 101348.88,
  "geography": "France",
  "tenure": 2,
  "balance": 119827.49,
  "numproducts": 1,
  "hascreditcard": true,
  "isactive": true
}
```

**Response Payload:**
```json
{
  "churn_probability": 0.174803,
  "churn_prediction": false,
  "threshold": 0.23,
  "cache_status": "cache_miss"
}
```

### 3. Prometheus Metrics Scrape
```http
GET /metrics
```
Exposes standard Prometheus scrape metrics including:
- `retainediq_http_requests_total{method="POST", path="/predict", status_code="200"}`
- `retainediq_http_request_duration_seconds`

---

## 📁 Repository Structure

```
RetainIQ/
├── app.py                     # Root multi-threaded runner (Backend + Frontend)
├── requirements.txt           # Python dependencies
├── docker-compose.yaml        # Docker stack (API, Redis, Postgres, Prometheus, Grafana)
├── dockerfile                 # FastAPI container build file
├── prometheus.yml             # Prometheus scrape configuration
├── artifacts/
│   ├── models/                # Trained LightGBM model artifact (lgbm_model.pkl)
│   ├── processed_data/        # Cleaned accounts, demographic, and location datasets
│   └── raw_data/              # Raw source datasets
├── backend/
│   ├── main.py                # FastAPI app initialization & middleware registration
│   ├── api/
│   │   ├── routes/            # Route controllers (health.py, predictions.py)
│   │   └── schemas/           # Pydantic data schemas (prediction.py)
│   ├── cache/                 # Redis caching client (redis_cache.py)
│   ├── core/                  # HTTP Basic Auth security guard (auth.py)
│   ├── middlewares/           # Prometheus request instrumentation (request_metrics.py)
│   └── services/              # ML inference service (prediction.py)
├── frontend/
│   ├── app.py                 # Streamlit entry point & navigation orchestrator
│   ├── config.py              # Application settings, presets & risk tiers
│   ├── api_client.py          # HTTP API client with local fallback support
│   ├── components/            # Reusable UI components (header, sidebar, cards, forms, charts)
│   ├── views/                 # Dashboard views (single, batch, insights, system_health)
│   └── utils/                 # Utilities (styling, helpers, retention AI)
├── pipeline/                  # End-to-end model training pipelines
├── scripts/                   # Data cleaning, ingestion, and downloading scripts
├── sql/                       # SQL table definitions and analytical EDA queries
└── src/                       # Core preprocessing and model training modules
```

---

