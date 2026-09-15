from __future__ import annotations

import json
import logging

from app.logging_config import (
    ContextFilter,
    JsonFormatter,
    clear_context,
    set_run_context,
)


def test_context_filter_adds_context_to_log_record() -> None:
    tokens = set_run_context(
        run_id="run-123",
        project_id="project-456",
        agent_name="researcher",
    )

    try:
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname=__file__,
            lineno=1,
            msg="hello",
            args=(),
            exc_info=None,
        )

        ContextFilter().filter(record)

        assert record.run_id == "run-123"
        assert record.project_id == "project-456"
        assert record.agent_name == "researcher"

    finally:
        clear_context(tokens)


def test_json_formatter_outputs_structured_log() -> None:
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="Agent finished",
        args=(),
        exc_info=None,
    )

    record.event = "agent.finished"
    record.duration_ms = 123.45

    formatted = JsonFormatter().format(record)
    payload = json.loads(formatted)

    assert payload["level"] == "INFO"
    assert payload["logger"] == "test"
    assert payload["message"] == "Agent finished"
    assert payload["event"] == "agent.finished"
    assert payload["duration_ms"] == 123.45


def test_json_formatter_works_with_plain_log_record() -> None:
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="hello",
        args=(),
        exc_info=None,
    )

    formatted = JsonFormatter().format(record)
    payload = json.loads(formatted)

    assert payload["level"] == "INFO"
    assert payload["logger"] == "test"
    assert payload["message"] == "hello"

    assert "run_id" not in payload
    assert "project_id" not in payload
    assert "agent_name" not in payload