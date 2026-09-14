from __future__ import annotations

import json
import uuid

from redis.asyncio import Redis


class RedisQueue:
    def __init__(
        self,
        redis: Redis,
        queue_name: str = "venture_lab:analysis",
    ):
        self.redis = redis
        self.queue_name = queue_name

    async def enqueue_run(
        self,
        run_id: uuid.UUID,
    ) -> None:
        message = {
            "type": "run_analysis",
            "run_id": str(run_id),
        }

        await self.redis.rpush(
            self.queue_name,
            json.dumps(message),
        )

    async def dequeue_run(self) -> dict | None:
        item = await self.redis.blpop(
            self.queue_name,
            timeout=5,
        )

        if item is None:
            return None

        _, message = item

        return json.loads(message)