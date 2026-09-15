from __future__ import annotations

import asyncio
import logging
import uuid
import signal
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from datetime import UTC, datetime
from app.worker.execution import run_analysis
from app.core.config import get_settings
from app.domain.enums import RunStatus
from app.infra.redis import create_redis_client
from app.models.run import Run
from app.queue.redis import RedisQueue
from app.repositories.run import RunRepository


logger = logging.getLogger(__name__)

def parse_run_id(message: dict) -> uuid.UUID:
    if message.get("type") != "run_analysis":
        raise ValueError(
            f"Unsupported message type: {message.get('type')!r}"
        )

    raw_run_id = message.get("run_id")

    if not isinstance(raw_run_id, str):
        raise ValueError("Message does not contain run_id")

    return uuid.UUID(raw_run_id)

async def process_run(
    session: AsyncSession,
    run_id: uuid.UUID,
    analysis_fn=run_analysis,
) -> None:
    repository = RunRepository(session)

    run = await repository.get_by_id(run_id)
    logger.info(
        "Processing run: run_id=%s, found=%s",
        run_id,
        run is not None,
    )

    if run is None:
        return

    if run.status is not RunStatus.QUEUED:
        return

    run.started_at = datetime.now(UTC)

    await repository.update_status(
        run,
        RunStatus.RUNNING,
    )

    await session.commit()
    logger.info(
        "Run %s -> running",
        run_id,
    )

    try:
        result = await analysis_fn(
            run.id,
            run.project_id,
            run.project.idea,
        )

        run.result = result
        run.finished_at = datetime.now(UTC)
        run.status = RunStatus.COMPLETED
        await session.commit()


    except Exception as exc:
        run.status = RunStatus.FAILED
        run.error = str(exc)
        run.finished_at = datetime.now(UTC)

        await session.commit()



async def main() -> None:
    settings = get_settings()
    stop_event = asyncio.Event()

    def request_shutdown() -> None:
        logger.info("Shutdown requested")
        stop_event.set()

    engine = create_async_engine(
        settings.async_database_url,
    )

    session_factory = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    redis = create_redis_client()
    queue = RedisQueue(redis)

    loop = asyncio.get_running_loop()

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, request_shutdown)

    try:
        while not stop_event.is_set():
            message = await queue.dequeue_run()

            if message is None:
                continue

            logger.info("Received message: %s", message)

            try:
                run_id = parse_run_id(message)
            except (ValueError, TypeError) as exc:
                logger.exception("Invalid queue message: %s", exc)
                continue

            async with session_factory() as session:
                await process_run(
                    session=session,
                    run_id=run_id,
                )
    finally:
        logger.info("Closing worker resources")
        await redis.aclose()
        await engine.dispose()




if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
    asyncio.run(main())