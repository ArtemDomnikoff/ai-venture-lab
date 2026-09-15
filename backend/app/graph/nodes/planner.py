from __future__ import annotations

from app.graph.schemas import ResearchPlan
from app.graph.state import AnalysisState
from app.llm.runner import generate_structured

SYSTEM_PROMPT = """
You are the planning node for a startup venture analysis system.

Create a focused research plan for the startup idea.

The plan must define five independent research tracks:

1. Market research
   - problem
   - demand
   - market trends
   - industry context
   - structural or regulatory factors

2. Customer research
   - ideal customer profile
   - pain points
   - jobs to be done
   - buying behavior
   - decision makers
   - willingness to pay

3. Competition research
   - direct competitors
   - indirect competitors
   - substitute solutions
   - pricing
   - positioning
   - differentiation

4. Technical research
   - technical feasibility
   - architecture
   - required technologies
   - data
   - integrations
   - security
   - scalability
   - implementation complexity

5. Business research
   - business model
   - monetization
   - pricing
   - unit economics
   - acquisition
   - margins
   - scalability
   - operational costs

Create a separate list of questions for each track.

Do not mix questions between tracks.
Do not judge the startup.
Do not invent facts.

Return only the structured research plan.
""".strip()


async def planner_node(state: AnalysisState) -> dict:
    plan = await generate_structured(
        system_prompt=SYSTEM_PROMPT,
        user_prompt=(
            "Create a research plan for this startup idea:\n\n"
            f"{state['idea']}"
        ),
        output_model=ResearchPlan,
    )

    return {
        "plan": plan,
    }