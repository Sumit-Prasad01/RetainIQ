import os
from functools import lru_cache

from fastapi import APIRouter, Depends, HTTPException, status

from backend.api.schemas.prediction import PredictionInput, PredictionResponse
from backend.cache.redis_cache import RedisCache
from backend.core.auth import require_user
from backend.services.prediction import ChurnPredictor

router = APIRouter(tags=["predictions"])
cache = RedisCache()
CACHE_TTL_SECONDS = int(os.getenv("PREDICTION_CACHE_TTL_SECONDS", "3600"))


@lru_cache
def get_predictor() -> ChurnPredictor:
    try:
        return ChurnPredictor()
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model artifact is not available",
        ) from exc


@router.post("/predict", response_model=PredictionResponse, summary="Predict customer churn")
def predict(
    payload: PredictionInput,
    _: str = Depends(require_user),
) -> PredictionResponse:
    key = ChurnPredictor.cache_key(payload)
    cached = cache.get(key)
    if cached is not None:
        return PredictionResponse(**cached, cache_status="cache_hit")

    prediction = get_predictor().predict(payload)
    saved = cache.set(key, prediction, CACHE_TTL_SECONDS)
    cache_status = "cache_miss" if saved else "cache_unavailable"
    return PredictionResponse(**prediction, cache_status=cache_status)
