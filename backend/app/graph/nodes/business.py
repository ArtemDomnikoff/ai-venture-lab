from __future__ import annotations

from app.graph.evidence import (
    build_search_context,
    validate_agent_evidence,
)
from app.graph.schemas import AgentFinding
from app.graph.state import AnalysisState
from app.llm.runner import generate_structured
from app.observability import agent_trace
from app.search.client import create_search_service

SYSTEM_PROMPT = """
You are the Business Agent in a multi-agent startup evaluation system.

Your job is to analyze the business model and economics
of the startup idea.

Focus on:
- revenue model;
- pricing;
- unit economics;
- cost structure;
- scalability;
- monetization risks.

Perform an independent analysis.

Use only supplied search evidence.

Evidence rules:
- Use only URLs returned by search.
- Do not invent revenue numbers, pricing,
  financial metrics, or business facts.
- Separate evidence-backed observations
  from assumptions.

Return:
- summary;
- claims;
- evidence;
- risks;
- opportunities;
- confidence.
""".strip()


async def business_node(
    state: AnalysisState,
) -> dict:

    plan = state["plan"]

    with agent_trace(
        agent_name="business",
        run_id=str(state.get("run_id", "")),
        project_id=str(state.get("project_id", "")),
        idea=state["idea"],
        input_data={
            "question_count": len(plan.business_questions),
            "business_focus": plan.business_focus,
        },
    ) as observation:
        search_service = create_search_service()

        query = (
            f"{state['idea']} "
            f"business model revenue pricing "
            f"unit economics monetization "
            f"scalability risks "
            f"{plan.business_focus}"
        )

        search_results = await search_service.search(
            query,
            max_results=5,
        )

        search_context = build_search_context(
            search_results,
        )

        questions = "\n".join(f"- {question}" for question in plan.business_questions)

        user_prompt = f"""
Startup idea:

{state["idea"]}

Business focus:

{plan.business_focus}

Research questions:

{questions}

External research:

{search_context}

Analyze:
- revenue model;
- pricing;
- scalability;
- monetization potential;
- economic risks.

Separate:
- evidence-backed findings;
- assumptions;
- risks;
- evidence gaps.
""".strip()

        result = await generate_structured(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            output_model=AgentFinding,
        )

        result = validate_agent_evidence(
            result,
            search_results,
        )

        if observation is not None:
            observation.update(
                output={
                    "claim_count": len(result.claims),
                    "evidence_count": len(result.evidence),
                    "confidence": result.confidence,
                }
            )

    return {
        "business": result,
    }
