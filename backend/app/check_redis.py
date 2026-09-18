import asyncio

from app.infra.redis import create_redis_client


async def main() -> None:
    redis = create_redis_client()

    try:
        result = await redis.ping()
        print(f"Redis OK: {result}")
    finally:
        await redis.aclose()


if __name__ == "__main__":
    asyncio.run(main())
