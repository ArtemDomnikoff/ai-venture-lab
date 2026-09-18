from collections.abc import AsyncGenerator

from fastapi import Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal
from app.infra.redis import create_redis_client
from app.queue.redis import RedisQueue


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
