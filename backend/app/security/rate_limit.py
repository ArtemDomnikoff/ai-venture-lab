from __future__ import annotations

import hashlib

from redis.asyncio import Redis


def email_rate_limit_key(
        email: str,
) -> str:
    normalized = email.strip().lower()

    digest = hashlib.sha256(
        normalized.encode(),
    ).hexdigest()

    return f"auth:email:{digest}"


class RateLimiter:
    _SCRIPT = """
    local current = redis.call("INCR", KEYS[1])

    if current == 1 then
        redis.call("EXPIRE", KEYS[1], ARGV[1])
    end

    local ttl = redis.call("TTL", KEYS[1])

    return {current, ttl}
    """

    def __init__(
        self,
        redis: Redis,
    ) -> None:
        self.redis = redis

    async def check(
        self,
        *,
        key: str,
        limit: int,
        window_seconds: int,
    ) -> tuple[bool, int]:
        result = await self.redis.eval(
            self._SCRIPT,
            1,
            key,
            window_seconds,
        )

        current = int(result[0])
        ttl = max(int(result[1]), 1)

        return current <= limit, ttl

    async def enforce(
        self,
        *,
        key: str,
        limit: int,
        window_seconds: int,
    ) -> None:
        from app.core.exceptions import RateLimitExceededError

        allowed, retry_after = await self.check(
            key=key,
            limit=limit,
            window_seconds=window_seconds,
        )

        if not allowed:
            raise RateLimitExceededError(
                retry_after=retry_after,
            )
