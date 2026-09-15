from __future__ import annotations

import os
import time
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

from langfuse import Langfuse, propagate_attributes

from app.core.config import get_settings
from app.logging_config import (
    clear_context,
    get_logger,
    set_run_context,
)


logger = get_logger(__name__)


_langfuse_client: Langfuse | None = None


def is_langfuse_enabled() -> bool:
    settings = get_settings()

    return bool(
        settings.langfuse_public_key
        and settings.langfuse_secret_key
    )


def get_langfuse() -> Langfuse | None:
    global _langfuse_client

    if not is_langfuse_enabled():
        return None

    if _langfuse_client is not None:
        return _langfuse_client

    settings = get_settings()

    os.environ["LANGFUSE_PUBLIC_KEY"] = (
        settings.langfuse_public_key
    )

    os.environ["LANGFUSE_SECRET_KEY"] = (
        settings.langfuse_secret_key
    )

    os.environ["LANGFUSE_BASE_URL"] = (
        settings.langfuse_base_url
    )

    os.environ["LANGFUSE_TRACING_ENVIRONMENT"] = (
        settings.langfuse_tracing_environment
    )

    _langfuse_client = Langfuse(
        public_key=settings.langfuse_public_key,
        secret_key=settings.langfuse_secret_key,
        base_url=settings.langfuse_base_url,
        environment=settings.langfuse_tracing_environment,
    )

    return _langfuse_client


@contextmanager
def analysis_trace(
    *,
    run_id: str,
    project_id: str,
    idea: str,
) -> Iterator[Any]:

    started_at = time.perf_counter()

    tokens = set_run_context(
        run_id=run_id,
        project_id=project_id,
    )

    langfuse = get_langfuse()

    if langfuse is None:
        try:
            yield None

        finally:
            clear_context(tokens)

        return

    with langfuse.start_as_current_observation(
        name="startup-analysis",
        as_type="chain",
        input={
            "idea": idea,
            "run_id": run_id,
            "project_id": project_id,
        },
        metadata={
            "application": "ai-venture-lab",
        },
    ) as trace:

        with propagate_attributes(
            metadata={
                "run_id": run_id,
                "project_id": project_id,
            },
            tags=[
                "startup-analysis",
            ],
            environment=(
                get_settings()
                .langfuse_tracing_environment
            ),
        ):

            succeeded = False

            try:
                yield trace
                succeeded = True

            except Exception as exc:
                trace.update(
                    level="ERROR",
                    status_message=str(exc),
                )

                raise

            finally:
                trace.update(
                    output={
                        "status": (
                            "completed"
                            if succeeded
                            else "failed"
                        ),
                        "duration_ms": _elapsed_ms(
                            started_at,
                        ),
                    }
                )

                langfuse.flush()
                clear_context(tokens)


@contextmanager
def agent_trace(
    *,
    agent_name: str,
    run_id: str,
    project_id: str,
    idea: str,
    input_data: dict[str, Any] | None = None,
) -> Iterator[Any]:

    started_at = time.perf_counter()

    tokens = set_run_context(
        run_id=run_id,
        project_id=project_id,
        agent_name=agent_name,
    )

    langfuse = get_langfuse()

    if langfuse is None:
        try:
            yield None

        finally:
            clear_context(tokens)

        return

    payload = {
        "agent": agent_name,
        "idea": idea,
        "run_id": run_id,
        "project_id": project_id,
    }

    if input_data:
        payload.update(input_data)

    with langfuse.start_as_current_observation(
        name=f"agent.{agent_name}",
        as_type="agent",
        input=payload,
        metadata={
            "agent_name": agent_name,
        },
    ) as observation:

        succeeded = False

        try:
            yield observation
            succeeded = True

        except Exception as exc:
            observation.update(
                level="ERROR",
                status_message=str(exc),
            )

            raise

        finally:
            observation.update(
                output={
                    "status": (
                        "completed"
                        if succeeded
                        else "failed"
                    ),
                    "duration_ms": _elapsed_ms(
                        started_at,
                    ),
                }
            )

            clear_context(tokens)


@contextmanager
def tool_trace(
    *,
    tool_name: str,
    input_data: dict[str, Any],
) -> Iterator[Any]:

    started_at = time.perf_counter()

    langfuse = get_langfuse()

    if langfuse is None:
        yield None
        return

    with langfuse.start_as_current_observation(
        name=f"tool.{tool_name}",
        as_type="tool",
        input=input_data,
        metadata={
            "tool_name": tool_name,
        },
    ) as observation:

        succeeded = False

        try:
            yield observation
            succeeded = True

        except Exception as exc:
            observation.update(
                level="ERROR",
                status_message=str(exc),
            )

            raise

        finally:
            observation.update(
                output={
                    "status": (
                        "completed"
                        if succeeded
                        else "failed"
                    ),
                    "duration_ms": _elapsed_ms(
                        started_at,
                    ),
                }
            )


def _elapsed_ms(
    started_at: float,
) -> float:

    return round(
        (
            time.perf_counter()
            - started_at
        ) * 1000,
        2,
    )