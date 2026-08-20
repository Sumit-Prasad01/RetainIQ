import json
import os
from typing import Any

import redis


class RedisCache:
    """A deliberately small JSON cache that degrades gracefully if Redis is offline."""

    def __init__(self) -> None:
        self.client = redis.Redis.from_url(
            os.getenv("REDIS_URL", "redis://localhost:6379/0"),
            decode_responses=True,
            socket_connect_timeout=1,
            socket_timeout=1,
        )

    def get(self, key: str) -> dict[str, Any] | None:
        try:
            value = self.client.get(key)
            return json.loads(value) if value else None
        except redis.RedisError:
            return None

    def set(self, key: str, value: dict[str, Any], ttl: int) -> bool:
        try:
            self.client.setex(key, ttl, json.dumps(value))
            return True
        except redis.RedisError:
            return False
