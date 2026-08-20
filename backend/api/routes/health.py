from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/", summary="Service status")
def root() -> dict[str, str]:
    return {"status": "RetainIQ Churn API"}


@router.get("/health", summary="Health probe")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
