"""Modular HTTP API Client for RetainIQ FastAPI Backend with graceful fallback."""

import time
from typing import Any, Dict, List, Optional, Tuple
import requests
from requests.auth import HTTPBasicAuth


class RetainIQApiClient:
    """Client for interacting with the RetainIQ Churn Prediction API."""

    def __init__(
        self,
        base_url: str = "http://127.0.0.1:8000",
        username: str = "admin",
        password: str = "change-me",
        timeout: float = 10.0,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.username = username
        self.password = password
        self.timeout = timeout
        self._local_predictor = None

    def _get_auth(self) -> HTTPBasicAuth:
        return HTTPBasicAuth(self.username, self.password)

    def _get_local_predictor(self) -> Any:
        """Lazy load the local ChurnPredictor for standalone fallback."""
        if self._local_predictor is None:
            try:
                from backend.services.prediction import ChurnPredictor
                self._local_predictor = ChurnPredictor()
            except Exception as exc:
                raise RuntimeError(f"Unable to initialize local model predictor: {exc}") from exc
        return self._local_predictor

    def check_health(self) -> Dict[str, Any]:
        """Perform a health probe against the API backend and measure latency."""
        url = f"{self.base_url}/health"
        started_at = time.perf_counter()
        try:
            response = requests.get(url, timeout=self.timeout)
            latency_ms = round((time.perf_counter() - started_at) * 1000, 2)
            if response.status_code == 200:
                data = response.json()
                return {
                    "online": True,
                    "status": data.get("status", "ok"),
                    "latency_ms": latency_ms,
                    "status_code": 200,
                    "error": None,
                }
            else:
                return {
                    "online": False,
                    "status": "unhealthy",
                    "latency_ms": latency_ms,
                    "status_code": response.status_code,
                    "error": f"HTTP {response.status_code}: {response.text}",
                }
        except requests.exceptions.RequestException as exc:
            latency_ms = round((time.perf_counter() - started_at) * 1000, 2)
            return {
                "online": False,
                "status": "offline",
                "latency_ms": latency_ms,
                "status_code": None,
                "error": str(exc),
            }

    def predict_direct(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Execute prediction locally via the backend ChurnPredictor service without network calls."""
        from backend.api.schemas.prediction import PredictionInput

        started_at = time.perf_counter()
        predictor = self._get_local_predictor()
        input_schema = PredictionInput(**payload)
        result = predictor.predict(input_schema)
        latency_ms = round((time.perf_counter() - started_at) * 1000, 2)

        return {
            "churn_probability": result["churn_probability"],
            "churn_prediction": result["churn_prediction"],
            "threshold": result["threshold"],
            "cache_status": "local_engine",
            "latency_ms": latency_ms,
            "source": "Local ML Engine (Standalone)",
            "success": True,
            "error": None,
        }

    def predict(
        self, payload: Dict[str, Any], allow_fallback: bool = True
    ) -> Dict[str, Any]:
        """Send a single customer prediction request to the FastAPI backend with optional fallback."""
        url = f"{self.base_url}/predict"
        started_at = time.perf_counter()

        try:
            response = requests.post(
                url,
                json=payload,
                auth=self._get_auth(),
                timeout=self.timeout,
                headers={"Content-Type": "application/json", "X-Client": "RetainIQ-Streamlit"},
            )
            latency_ms = round((time.perf_counter() - started_at) * 1000, 2)

            if response.status_code == 200:
                data = response.json()
                return {
                    "churn_probability": float(data["churn_probability"]),
                    "churn_prediction": bool(data["churn_prediction"]),
                    "threshold": float(data["threshold"]),
                    "cache_status": data.get("cache_status", "cache_unavailable"),
                    "latency_ms": latency_ms,
                    "source": "FastAPI Service",
                    "success": True,
                    "error": None,
                }
            elif response.status_code == 401:
                return {
                    "success": False,
                    "error": "Authentication Failed (401 Unauthorized): Check API username & password in sidebar settings.",
                    "latency_ms": latency_ms,
                }
            else:
                if allow_fallback:
                    fallback_res = self.predict_direct(payload)
                    fallback_res["fallback_reason"] = f"Backend returned HTTP {response.status_code}: {response.text}"
                    return fallback_res
                return {
                    "success": False,
                    "error": f"API Error (HTTP {response.status_code}): {response.text}",
                    "latency_ms": latency_ms,
                }

        except requests.exceptions.RequestException as exc:
            latency_ms = round((time.perf_counter() - started_at) * 1000, 2)
            if allow_fallback:
                try:
                    fallback_res = self.predict_direct(payload)
                    fallback_res["fallback_reason"] = f"FastAPI backend unreachable ({exc}). Switched to local model engine."
                    return fallback_res
                except Exception as fallback_exc:
                    return {
                        "success": False,
                        "error": f"Network Error: {exc} | Local fallback also failed: {fallback_exc}",
                        "latency_ms": latency_ms,
                    }
            return {
                "success": False,
                "error": f"Cannot connect to API at {self.base_url} ({exc})",
                "latency_ms": latency_ms,
            }

    def predict_batch(
        self,
        records: List[Dict[str, Any]],
        progress_callback: Optional[Any] = None,
        allow_fallback: bool = True,
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """Process a list of customer records sequentially with progress tracking and aggregated stats."""
        results: List[Dict[str, Any]] = []
        cache_hits = 0
        cache_misses = 0
        errors = 0
        total_time_ms = 0.0

        for idx, record in enumerate(records):
            res = self.predict(record, allow_fallback=allow_fallback)
            results.append(res)
            if res.get("success"):
                status = res.get("cache_status")
                if status == "cache_hit":
                    cache_hits += 1
                elif status == "cache_miss":
                    cache_misses += 1
                total_time_ms += res.get("latency_ms", 0.0)
            else:
                errors += 1

            if progress_callback:
                progress_callback(idx + 1, len(records))

        summary = {
            "total": len(records),
            "successful": len(records) - errors,
            "failed": errors,
            "cache_hits": cache_hits,
            "cache_misses": cache_misses,
            "avg_latency_ms": round(total_time_ms / max(len(records) - errors, 1), 2),
        }
        return results, summary

    def get_metrics_text(self) -> Tuple[bool, str]:
        """Fetch raw Prometheus metrics from /metrics endpoint."""
        url = f"{self.base_url}/metrics"
        try:
            response = requests.get(url, timeout=self.timeout)
            if response.status_code == 200:
                return True, response.text
            return False, f"HTTP {response.status_code}: {response.text}"
        except requests.exceptions.RequestException as exc:
            return False, str(exc)
