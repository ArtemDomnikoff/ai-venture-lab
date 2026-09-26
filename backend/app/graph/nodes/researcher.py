from __future__ import annotations

from app.graph.research import run_research_agent
from app.graph.state import AnalysisState


async def researcher_node(
    state: AnalysisState,
) -> dict:
    plan = state["plan"]

    result = await run_research_agent(
        state,
        agent_key="researcher",
        questions=plan.market_questions,
        queries=plan.market_queries,
        focus=plan.market_focus,
    )

    return {
        "researcher": result,
    }
