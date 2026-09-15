from __future__ import annotations

import uuid

from app.observability import (
    analysis_trace,
    agent_trace,
    generation_trace,
    tool_trace,
    get_langfuse,
    is_langfuse_enabled,
)


AGENTS = [
    "planner",
    "researcher",
    "customer",
    "competitor",
    "tech",
    "business",
    "skeptic",
    "judge",
]


def fake_generation(
    name: str,
):
    with generation_trace(
        name=f"llm.{name}.mock",
        model="mock-model",
        input_data={
            "provider": "mock",
            "tokens": 0,
        },
    ) as generation:

        if generation:
            generation.update(
                output={
                    "status": "mock_success",
                },
                usage_details={
                    "input": 0,
                    "output": 0,
                    "total": 0,
                },
            )


def fake_tavily():
    with tool_trace(
        tool_name="tavily.search.mock",
        input_data={
            "query": "startup analysis",
            "provider": "mock",
        },
    ) as tool:

        if tool:
            tool.update(
                output={
                    "results": 5,
                }
            )


def main():

    if not is_langfuse_enabled():
        raise RuntimeError(
            "Langfuse is not configured"
        )

    langfuse = get_langfuse()

    if langfuse is None:
        raise RuntimeError(
            "Langfuse unavailable"
        )


    run_id = str(uuid.uuid4())
    project_id = str(uuid.uuid4())


    with analysis_trace(
        run_id=run_id,
        project_id=project_id,
        idea="Mock startup analysis",
    ):


        for agent in AGENTS:

            with agent_trace(
                agent_name=agent,
                run_id=run_id,
                project_id=project_id,
                idea="Mock startup analysis",
            ):


                if agent in {
                    "researcher",
                    "customer",
                    "competitor",
                    "tech",
                    "business",
                }:
                    fake_tavily()


                fake_generation(
                    agent,
                )


    langfuse.flush()


    print(
        "Full Langfuse observation smoke test OK"
    )

    print(
        f"run_id={run_id}"
    )


if __name__ == "__main__":
    main()