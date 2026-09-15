from __future__ import annotations

import uuid

from app.observability import (
    agent_trace,
    analysis_trace,
    generation_trace,
    get_langfuse,
    is_langfuse_enabled,
    tool_trace,
)


IDEA = "Smoke test startup idea"


def run_agent(
    *,
    name: str,
    run_id: str,
    project_id: str,
    use_search: bool = False,
) -> None:
    with agent_trace(
        agent_name=name,
        run_id=run_id,
        project_id=project_id,
        idea=IDEA,
    ):

        if use_search:
            with tool_trace(
                tool_name="tavily.search",
                input_data={
                    "query": f"{name} research query",
                    "max_results": 5,
                },
            ) as tool:

                if tool is not None:
                    tool.update(
                        output={
                            "results": 5,
                            "status": "mocked",
                        }
                    )

        with generation_trace(
            name="llm.generate_structured",
            model="smoke-test-model",
            input_data={
                "agent": name,
            },
        ) as generation:

            if generation is not None:
                generation.update(
                    output={
                        "status": "mocked",
                        "agent": name,
                    }
                )


def main() -> None:
    if not is_langfuse_enabled():
        raise RuntimeError(
            "Langfuse is not configured"
        )

    langfuse = get_langfuse()

    if langfuse is None:
        raise RuntimeError(
            "Langfuse client was not created"
        )

    if not langfuse.auth_check():
        raise RuntimeError(
            "Langfuse authentication failed"
        )


    run_id = str(uuid.uuid4())
    project_id = str(uuid.uuid4())


    with analysis_trace(
        run_id=run_id,
        project_id=project_id,
        idea=IDEA,
    ):

        #
        # Planner
        #
        run_agent(
            name="planner",
            run_id=run_id,
            project_id=project_id,
        )


        #
        # Five parallel branches
        #
        # В реальном LangGraph они будут идти
        # параллельно через fan-out.
        # Здесь мы просто создаём одинаковую
        # структуру spans.
        #

        run_agent(
            name="researcher",
            run_id=run_id,
            project_id=project_id,
            use_search=True,
        )

        run_agent(
            name="customer",
            run_id=run_id,
            project_id=project_id,
            use_search=True,
        )

        run_agent(
            name="competitor",
            run_id=run_id,
            project_id=project_id,
            use_search=True,
        )

        run_agent(
            name="tech",
            run_id=run_id,
            project_id=project_id,
            use_search=True,
        )

        run_agent(
            name="business",
            run_id=run_id,
            project_id=project_id,
            use_search=True,
        )


        #
        # Final aggregation
        #

        run_agent(
            name="skeptic",
            run_id=run_id,
            project_id=project_id,
        )

        run_agent(
            name="judge",
            run_id=run_id,
            project_id=project_id,
        )


    langfuse.flush()


    print(
        "Langfuse observation smoke test: OK"
    )

    print(
        f"run_id: {run_id}"
    )

    print(
        """
Expected Langfuse tree:

startup-analysis
│
├── agent.planner
│   └── llm.generate_structured
│
├── agent.researcher
│   ├── tool.tavily.search
│   └── llm.generate_structured
│
├── agent.customer
│   ├── tool.tavily.search
│   └── llm.generate_structured
│
├── agent.competitor
│   ├── tool.tavily.search
│   └── llm.generate_structured
│
├── agent.tech
│   ├── tool.tavily.search
│   └── llm.generate_structured
│
├── agent.business
│   ├── tool.tavily.search
│   └── llm.generate_structured
│
├── agent.skeptic
│   └── llm.generate_structured
│
└── agent.judge
    └── llm.generate_structured
"""
    )


if __name__ == "__main__":
    main()