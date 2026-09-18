import asyncio
import uuid

from app.infra.redis import create_redis_client
from app.queue.redis import RedisQueue


async def main() -> None:
    redis = create_redis_client()
    queue = RedisQueue(redis)

    try:
        await redis.delete(queue.queue_name)

        run_id = uuid.uuid4()

        await queue.enqueue_run(run_id)

        print(f"run_id: {run_id}")

        messages = await redis.lrange(
            queue.queue_name,
            0,
            -1,
        )

        print(f"messages: {messages}")
    finally:
        await redis.aclose()


if __name__ == "__main__":
    asyncio.run(main())
