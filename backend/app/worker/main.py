from __future__ import annotations

import asyncio
import logging
import signal
import uuid
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import get_settings
from app.domain.enums import RunStatus
from app.infra.redis import create_redis_client
from app.logging_config import configure_logging
from app.queue.redis import RedisQueue
from app.repositories.run import RunRepository
from app.worker.execution import run_analysis

logger = logging.getLogger(__name__)


def parse_run_id(
    message: dict,
) -> uuid.UUID:
    if message.get("type") != "run_analysis":
        raise ValueError(f"Unsupported message type: {message.get('type')!r}")

    raw_run_id = message.get("run_id")

    if not isinstance(raw_run_id, str):
        raise TypeError("Message does not contain run_id")

    return uuid.UUID(raw_run_id)


async def process_run(
    session: AsyncSession,
    run_id: uuid.UUID,
    analysis_fn=run_analysis,
) -> None:
    repository = RunRepository(session)

    run = await repository.get_by_id(
        run_id,
    )

    logger.info(
        "Run received",
        extra={
            "event": "run.received",
        },
    )

    if run is None:
        logger.warning(
            "Run not found",
            extra={
                "event": "run.not_found",
            },
        )
        return

    if run.status is not RunStatus.QUEUED:
        logger.info(
            "Run skipped because it is not queued",
            extra={
                "event": "run.skipped",
            },
        )
        return

    run.started_at = datetime.now(UTC)

    await repository.update_status(
        run,
        RunStatus.RUNNING,
    )

    await session.commit()

    logger.info(
        "Run marked as running",
        extra={
            "event": "run.running",
        },
    )

    try:
        result = await analysis_fn(
            session,
            run.id,
            run.project_id,
            run.project.idea,
        )

        run.result = result
        run.finished_at = datetime.now(UTC)

        await repository.update_status(
            run,
            RunStatus.COMPLETED,
        )

        await session.commit()

        logger.info(
            "Run completed",
            extra={
                "event": "run.completed",
            },
        )

    except Exception as exc:
        run.error = str(exc)
        run.finished_at = datetime.now(UTC)

        await repository.update_status(
            run,
            RunStatus.FAILED,
        )

        await session.commit()

        logger.exception(
            "Run failed",
            extra={
                "event": "run.failed",
            },
        )


async def main() -> None:
    configure_logging()

    settings = get_settings()
    stop_event = asyncio.Event()

    def request_shutdown() -> None:
        logger.info(
            "Shutdown requested",
            extra={
                "event": "worker.shutdown_requested",
            },
        )
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

    for sig in (
        signal.SIGINT,
        signal.SIGTERM,
    ):
        loop.add_signal_handler(
            sig,
            request_shutdown,
        )

    logger.info(
        "Worker started",
        extra={
            "event": "worker.started",
        },
    )

    try:
        while not stop_event.is_set():
            message = await queue.dequeue_run()

            if message is None:
                continue

            logger.info(
                "Queue message received",
                extra={
                    "event": "queue.message_received",
                },
            )

            try:
                run_id = parse_run_id(
                    message,
                )

            except (ValueError, TypeError):
                logger.exception(
                    "Invalid queue message",
                    extra={
                        "event": "queue.invalid_message",
                    },
                )
                continue

            async with session_factory() as session:
                await process_run(
                    session=session,
                    run_id=run_id,
                )

    finally:
        logger.info(
            "Worker shutting down",
            extra={
                "event": "worker.shutdown",
            },
        )

        await redis.aclose()
        await engine.dispose()

        logger.info(
            "Worker stopped",
            extra={
                "event": "worker.stopped",
            },
        )


if __name__ == "__main__":
    configure_logging()
    asyncio.run(main())
