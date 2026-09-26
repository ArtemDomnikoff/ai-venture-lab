from __future__ import annotations

from app.graph.research import run_research_agent
from app.graph.state import AnalysisState


async def competitor_node(
    state: AnalysisState,
) -> dict:
    plan = state["plan"]

    result = await run_research_agent(
        state,
        agent_key="competitor",
        questions=plan.competition_questions,
        queries=plan.competition_queries,
        focus=plan.competition_focus,
    )

    return {
        "competitor": result,
    }
