from __future__ import annotations

import json
import uuid

import pytest

from app.infra.redis import create_redis_client
from app.queue.redis import RedisQueue


@pytest.mark.asyncio
async def test_enqueue_run() -> None:
    redis = create_redis_client()

    queue = RedisQueue(
        redis,
        queue_name="venture_lab:test:analysis",
    )

    run_id = uuid.uuid4()

    await redis.delete(queue.queue_name)

    await queue.enqueue_run(run_id)

    message = await redis.lpop(queue.queue_name)

    assert message is not None

    assert json.loads(message) == {
        "type": "run_analysis",
        "run_id": str(run_id),
    }

    await redis.delete(queue.queue_name)
    await redis.aclose()


@pytest.mark.asyncio
async def test_dequeue_run() -> None:
    redis = create_redis_client()

    queue = RedisQueue(
        redis,
        queue_name="venture_lab:test:analysis",
    )

    run_id = uuid.uuid4()

    await redis.delete(queue.queue_name)

    await queue.enqueue_run(run_id)

    message = await queue.dequeue_run()

    assert message == {
        "type": "run_analysis",
        "run_id": str(run_id),
    }

    await redis.delete(queue.queue_name)
    await redis.aclose()
