from dotenv import load_dotenv

# Load local configuration before importing modules that read environment settings.
load_dotenv()

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from backend.middlewares import RequestMetricsMiddleware
from backend.api.routes import api_router

app = FastAPI(title="RetainIQ Churn API", version="1.0.0")
app.add_middleware(RequestMetricsMiddleware)
app.include_router(api_router)

# Metrics are intentionally unauthenticated so Prometheus can scrape this endpoint.
Instrumentator(excluded_handlers=["/metrics"]).instrument(app).expose(app, include_in_schema=False)
