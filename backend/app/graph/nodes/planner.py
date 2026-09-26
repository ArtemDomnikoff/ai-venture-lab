from __future__ import annotations

from app.graph.schemas import ResearchPlan
from app.graph.state import AnalysisState
from app.llm.runner import generate_structured
from app.observability import agent_trace

SYSTEM_PROMPT = """
You are the Planner node in a multi-agent startup research system.

Create an investigation plan for five independent research tracks:

1. Market
2. Customer
3. Competition
4. Technology
5. Business

For every track produce:
- 3-6 concrete research questions;
- 4-5 targeted web-search queries;
- one concise research focus.

Search queries are not generic topic labels. Each query must be designed to
retrieve specific evidence needed to answer one or more research questions.

Good queries usually include:
- the exact problem/category;
- a measurable fact;
- a relevant buyer or segment;
- a competitor/company;
- a pricing or adoption term;
- a technical mechanism;
- a time period or geography when those are explicitly relevant.

Do not invent geography, customer segments, competitors, prices, or market facts.
Only use geography or specificity that can be reasonably derived from the idea.
When specificity is unknown, formulate a query that discovers it.

For each track include both questions and search queries.
Do not perform research.
Return only the structured research plan.
""".strip()


async def planner_node(
    state: AnalysisState,
) -> dict:
    idea = state["idea"]

    user_prompt = f"""
Startup idea:

{idea}

Create the research plan.

The questions must describe what we need to know.
The search queries must describe what we should actually search for.
Avoid generic queries such as "market trends" or "startup opportunity".
""".strip()

    with agent_trace(
        agent_name="planner",
        run_id=str(
            state.get(
                "run_id",
                "",
            )
        ),
        project_id=str(
            state.get(
                "project_id",
                "",
            )
        ),
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
                    "market_questions": len(
                        result.market_questions,
                    ),
                    "market_queries": len(
                        result.market_queries,
                    ),
                    "customer_questions": len(
                        result.customer_questions,
                    ),
                    "customer_queries": len(
                        result.customer_queries,
                    ),
                    "competition_questions": len(
                        result.competition_questions,
                    ),
                    "competition_queries": len(
                        result.competition_queries,
                    ),
                    "tech_questions": len(
                        result.tech_questions,
                    ),
                    "tech_queries": len(
                        result.tech_queries,
                    ),
                    "business_questions": len(
                        result.business_questions,
                    ),
                    "business_queries": len(
                        result.business_queries,
                    ),
                }
            )

        return {
            "plan": result,
        }
