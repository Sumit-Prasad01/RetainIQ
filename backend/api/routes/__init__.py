"""Route registration for the RetainIQ API."""

from fastapi import APIRouter

from backend.api.routes.health import router as health_router
from backend.api.routes.predictions import router as predictions_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(predictions_router)

__all__ = ["api_router"]
