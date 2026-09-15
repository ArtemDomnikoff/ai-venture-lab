from __future__ import annotations

import asyncio
import uuid

from app.worker.execution import run_analysis


async def main():
    result = await run_analysis(
        run_id=uuid.uuid4(),
        project_id=uuid.uuid4(),
        idea="AI startup evaluator",
    )

    print("DONE")
    print(result["judge"])


if __name__ == "__main__":
    asyncio.run(main())