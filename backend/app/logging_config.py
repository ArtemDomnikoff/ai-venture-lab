from __future__ import annotations

import json
import logging
import sys
from contextvars import ContextVar, Token
from datetime import UTC, datetime
from typing import Any


_run_id: ContextVar[str | None] = ContextVar(
    "run_id",
    default=None,
)

_project_id: ContextVar[str | None] = ContextVar(
    "project_id",
    default=None,
)

_agent_name: ContextVar[str | None] = ContextVar(
    "agent_name",
    default=None,
)


class ContextFilter(logging.Filter):
    def filter(
        self,
        record: logging.LogRecord,
    ) -> bool:
        record.run_id = _run_id.get()
        record.project_id = _project_id.get()
        record.agent_name = _agent_name.get()

        return True


class JsonFormatter(logging.Formatter):
    def format(
        self,
        record: logging.LogRecord,
    ) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        fields = (
            "run_id",
            "project_id",
            "agent_name",
            "event",
            "duration_ms",
            "result_count",
            "claim_count",
            "evidence_count",
            "score",
            "model",
            "input_tokens",
            "output_tokens",
            "total_tokens",
            "cached_tokens",
            "reasoning_tokens",
        )

        for field in fields:
            value = getattr(record, field, None)

            if value is not None:
                payload[field] = value

        if record.exc_info:
            payload["exception"] = self.formatException(
                record.exc_info,
            )

        return json.dumps(
            payload,
            ensure_ascii=False,
        )


def configure_logging(
    *,
    level: int = logging.INFO,
) -> None:
    handler = logging.StreamHandler(sys.stdout)

    handler.setFormatter(
        JsonFormatter(),
    )

    handler.addFilter(
        ContextFilter(),
    )

    root_logger = logging.getLogger()

    root_logger.setLevel(level)
    root_logger.handlers.clear()
    root_logger.addHandler(handler)


def set_run_context(
    *,
    run_id: str | None = None,
    project_id: str | None = None,
    agent_name: str | None = None,
) -> list[tuple[ContextVar[Any], Token[Any]]]:
    tokens: list[
        tuple[ContextVar[Any], Token[Any]]
    ] = []

    if run_id is not None:
        token = _run_id.set(run_id)
        tokens.append(
            (_run_id, token),
        )

    if project_id is not None:
        token = _project_id.set(project_id)
        tokens.append(
            (_project_id, token),
        )

    if agent_name is not None:
        token = _agent_name.set(agent_name)
        tokens.append(
            (_agent_name, token),
        )

    return tokens


def clear_context(
    tokens: list[
        tuple[ContextVar[Any], Token[Any]]
    ],
) -> None:
    for context_var, token in reversed(tokens):
        context_var.reset(token)


def get_logger(
    name: str,
) -> logging.Logger:
    return logging.getLogger(name)