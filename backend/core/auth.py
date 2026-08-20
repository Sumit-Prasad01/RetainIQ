import hmac
import os

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

security = HTTPBasic()


def require_user(credentials: HTTPBasicCredentials = Depends(security)) -> str:
    """Small HTTP Basic auth guard for this internal API."""
    expected_username = os.getenv("API_USERNAME", "admin")
    expected_password = os.getenv("API_PASSWORD", "change-me")

    is_valid = hmac.compare_digest(credentials.username, expected_username) and hmac.compare_digest(
        credentials.password, expected_password
    )
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username
