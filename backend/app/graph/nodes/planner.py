from __future__ import annotations

from app.graph.schemas import ResearchPlan
from app.graph.state import AnalysisState
from app.llm.runner import generate_structured
from app.observability import agent_trace


SYSTEM_PROMPT = """
You are the Planner node in a multi-agent startup evaluation system.

Your job is to create a research plan for five independent analytical tracks:

1. Market
2. Customer
3. Competition
4. Technology
5. Business

The five analytical agents must work independently.
Do not create dependencies between these tracks.

For each track, produce:
- focused research questions;
- a concise research focus.

The final plan must contain separate question lists for:
- market_questions
- customer_questions
- competition_questions
- tech_questions
- business_questions

The plan must also contain:
- market_focus
- customer_focus
- competition_focus
- tech_focus
- business_focus

Do not perform the actual research.
Do not invent facts about the startup or its market.

Return only the structured research plan.
""".strip()


async def planner_node(state: AnalysisState) -> dict:
    idea = state["idea"]

    user_prompt = f"""
Startup idea:

{idea}

Create an independent research plan for the five analytical tracks:
market, customer, competition, technology, and business.

Make the research questions concrete enough for specialized agents
to investigate them independently.
""".strip()

    with agent_trace(
        agent_name="planner",
        run_id=str(state.get("run_id", "")),
        project_id=str(state.get("project_id", "")),
        idea=idea,
    ) as observation:
        result = await generate_structured(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            output_model=ResearchPlan,
        )

        if observation is not None:
            observation.update(
                output={
                    "market_questions": len(result.market_questions),
                    "customer_questions": len(result.customer_questions),
                    "competition_questions": len(result.competition_questions),
                    "tech_questions": len(result.tech_questions),
                    "business_questions": len(result.business_questions),
                }
            )

        return {
            "plan": result,
        }