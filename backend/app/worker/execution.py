from __future__ import annotations

import asyncio
import uuid


async def mock_analysis(run_id: uuid.UUID) -> dict:
    await asyncio.sleep(1)

    return {
        "message": "Mock analysis completed",
        "score": 50,
        "run_id": str(run_id),
    }