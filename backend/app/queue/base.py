from __future__ import annotations

import uuid
from typing import Protocol


class Queue(Protocol):
    async def enqueue_run(
        self,
        run_id: uuid.UUID,
    ) -> None:
        ...