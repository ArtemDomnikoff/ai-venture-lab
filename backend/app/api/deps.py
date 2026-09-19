from __future__ import annotations

from collections.abc import AsyncGenerator
from datetime import UTC, datetime
from hashlib import sha256

from fastapi import Depends, Request
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.exceptions import UnauthorizedError
from app.db.session import AsyncSessionLocal
from app.infra.redis import create_redis_client
from app.models import User
from app.queue.redis import RedisQueue
from app.repositories.user import UserRepository
from app.repositories.user_session import UserSessionRepository
from app.security.rate_limit import RateLimiter


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


async def get_redis() -> AsyncGenerator[Redis, None]:
    redis = create_redis_client()

    try:
        yield redis
    finally:
        await redis.aclose()


async def get_queue(
    redis: Redis = Depends(get_redis),
) -> RedisQueue:
    return RedisQueue(redis)


async def get_rate_limiter(
    redis: Redis = Depends(get_redis),
) -> RateLimiter:
    return RateLimiter(redis)


async def get_current_user(
        request: Request,
        session: AsyncSession = Depends(get_session),
) -> User:
    settings = get_settings()

    token = request.cookies.get(
        settings.auth_cookie_name,
    )

    if not token:
        raise UnauthorizedError()

    token_hash = sha256(
        token.encode(),
    ).hexdigest()
    session_repository = UserSessionRepository(
        session,
    )

    user_session = (
        await session_repository.get_by_token_hash(
            token_hash,
        )
    )

    if user_session is None:
        raise UnauthorizedError()

    if user_session.expires_at <= datetime.now(UTC):
        await session_repository.delete_by_token_hash(
            token_hash,
        )

        await session.commit()

        raise UnauthorizedError()

    user = await UserRepository(
        session,
    ).get_by_id(
        user_session.user_id,
    )

    if user is None:
        raise UnauthorizedError()

    return user
