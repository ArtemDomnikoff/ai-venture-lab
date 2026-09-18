from __future__ import annotations

import uuid

import pytest

from app.observability import (
    agent_trace,
    analysis_trace,
    tool_trace,
)


@pytest.mark.asyncio
async def test_analysis_trace_is_noop_during_tests() -> None:
    run_id = str(uuid.uuid4())
    project_id = str(uuid.uuid4())

    with analysis_trace(
        run_id=run_id,
        project_id=project_id,
        idea="Observability test",
    ) as observation:
        assert observation is None

        with agent_trace(
            agent_name="researcher",
            run_id=run_id,
            project_id=project_id,
            idea="Observability test",
        ) as agent_observation:
            assert agent_observation is None

            with tool_trace(
                tool_name="tavily.search",
                input_data={
                    "query": "observability test",
                },
            ) as tool_observation:
                assert tool_observation is None


@pytest.mark.asyncio
async def test_observability_contexts_do_not_raise_when_disabled() -> None:
    run_id = str(uuid.uuid4())
    project_id = str(uuid.uuid4())

    with (
        analysis_trace(
            run_id=run_id,
            project_id=project_id,
            idea="Observability test",
        ),
        agent_trace(
            agent_name="researcher",
            run_id=run_id,
            project_id=project_id,
            idea="Observability test",
        ),
        tool_trace(
            tool_name="tavily.search",
            input_data={
                "query": "observability test",
            },
        ),
    ):
        pass
