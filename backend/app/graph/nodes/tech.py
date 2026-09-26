from __future__ import annotations

from app.graph.research import run_research_agent
from app.graph.state import AnalysisState


async def tech_node(
    state: AnalysisState,
) -> dict:
    plan = state["plan"]

    result = await run_research_agent(
        state,
        agent_key="tech",
        questions=plan.tech_questions,
        queries=plan.tech_queries,
        focus=plan.tech_focus,
    )

    return {
        "tech": result,
    }
