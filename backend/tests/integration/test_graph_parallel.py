from __future__ import annotations

import asyncio

import pytest
from langgraph.graph import END, START, StateGraph

from app.graph.state import AnalysisState


@pytest.mark.asyncio
async def test_five_agents_run_in_parallel_before_skeptic() -> None:
    active_agents = 0
    max_active_agents = 0
    completed_agents: list[str] = []
    skeptic_started = False

    async def planner(state):
        return {"plan": {"ready": True}}

    async def analyst(name: str, state):
        nonlocal active_agents, max_active_agents

        active_agents += 1
        max_active_agents = max(
            max_active_agents,
            active_agents,
        )

        await asyncio.sleep(0.02)

        completed_agents.append(name)
        active_agents -= 1

        return {name: {"done": True}}

    async def skeptic(state):
        nonlocal skeptic_started

        skeptic_started = True

        assert len(completed_agents) == 5
        assert active_agents == 0

        return {"skeptic": {"done": True}}

    async def researcher(state):
        return await analyst("researcher", state)

    async def customer(state):
        return await analyst("customer", state)

    async def competitor(state):
        return await analyst("competitor", state)

    async def tech(state):
        return await analyst("tech", state)

    async def business(state):
        return await analyst("business", state)

    graph = StateGraph(AnalysisState)

    graph.add_node("planner", planner)

    graph.add_node("researcher", researcher)
    graph.add_node("customer", customer)
    graph.add_node("competitor", competitor)
    graph.add_node("tech", tech)
    graph.add_node("business", business)

    graph.add_node("skeptic", skeptic)

    graph.add_edge(START, "planner")

    graph.add_edge("planner", "researcher")
    graph.add_edge("planner", "customer")
    graph.add_edge("planner", "competitor")
    graph.add_edge("planner", "tech")
    graph.add_edge("planner", "business")

    graph.add_edge("researcher", "skeptic")
    graph.add_edge("customer", "skeptic")
    graph.add_edge("competitor", "skeptic")
    graph.add_edge("tech", "skeptic")
    graph.add_edge("business", "skeptic")

    graph.add_edge("skeptic", END)

    compiled = graph.compile()

    result = await compiled.ainvoke(
        {
            "idea": "AI venture evaluator",
        }
    )

    assert max_active_agents == 5
    assert len(completed_agents) == 5
    assert skeptic_started is True
    assert result["skeptic"] == {"done": True}