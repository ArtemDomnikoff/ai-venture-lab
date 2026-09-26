from __future__ import annotations

from app.graph.research import run_research_agent
from app.graph.state import AnalysisState


async def business_node(
    state: AnalysisState,
) -> dict:
    plan = state["plan"]

    result = await run_research_agent(
        state,
        agent_key="business",
        questions=plan.business_questions,
        queries=plan.business_queries,
        focus=plan.business_focus,
    )

    return {
        "business": result,
    }
