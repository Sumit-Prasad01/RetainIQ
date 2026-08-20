"""Request correlation and Prometheus metrics middleware."""

from time import perf_counter
from uuid import uuid4

from fastapi import Request
from prometheus_client import Counter, Histogram
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

HTTP_REQUESTS_TOTAL = Counter(
    "retainediq_http_requests_total",
    "Number of HTTP requests handled by RetainIQ.",
    ("method", "path", "status_code"),
)
HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "retainediq_http_request_duration_seconds",
    "Time spent handling RetainIQ HTTP requests.",
    ("method", "path"),
)


class RequestMetricsMiddleware(BaseHTTPMiddleware):
    """Attach a request id and record bounded-cardinality HTTP metrics."""

    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):  # type: ignore[no-untyped-def]
        request_id = request.headers.get("X-Request-ID", str(uuid4()))
        started_at = perf_counter()
        response = await call_next(request)

        route = request.scope.get("route")
        path = getattr(route, "path", request.url.path)
        duration = perf_counter() - started_at
        if path != "/metrics":
            HTTP_REQUESTS_TOTAL.labels(request.method, path, response.status_code).inc()
            HTTP_REQUEST_DURATION_SECONDS.labels(request.method, path).observe(duration)

        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = f"{duration:.6f}"
        return response
