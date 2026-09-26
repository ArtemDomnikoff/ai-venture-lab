from __future__ import annotations

from app.graph.research import run_research_agent
from app.graph.state import AnalysisState


async def customer_node(
    state: AnalysisState,
) -> dict:
    plan = state["plan"]

    result = await run_research_agent(
        state,
        agent_key="customer",
        questions=plan.customer_questions,
        queries=plan.customer_queries,
        focus=plan.customer_focus,
    )

    return {
        "customer": result,
    }
