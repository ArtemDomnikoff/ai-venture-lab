from __future__ import annotations

from redis.asyncio import Redis

from app.core.config import get_settings


def create_redis_client() -> Redis:
    settings = get_settings()

    return Redis.from_url(
        settings.redis_url,
        decode_responses=True,
        socket_timeout=None,
        socket_connect_timeout=5,
    )
