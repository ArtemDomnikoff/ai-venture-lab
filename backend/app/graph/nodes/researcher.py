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
You are the Market Research Agent in an AI startup evaluation system.

Your job is to independently investigate the market opportunity behind
the startup idea.

Analyze:
- market size and structure;
- market growth;
- important trends;
- demand drivers;
- adoption dynamics;
- industry changes;
- market risks.

Use only the supplied web research as factual evidence.

Do not invent:
- statistics;
- market sizes;
- growth rates;
- companies;
- URLs;
- citations.

If evidence is insufficient, explicitly state the limitation.

Return:
- summary;
- claims;
- evidence;
- risks;
- opportunities;
- confidence.
""".strip()


async def researcher_node(
    state: AnalysisState,
) -> dict:

    plan = state["plan"]

    with agent_trace(
        agent_name="researcher",
        run_id=str(
            state.get("run_id", "")
        ),
        project_id=str(
            state.get("project_id", "")
        ),
        idea=state["idea"],
        input_data={
            "question_count": len(
                plan.market_questions
            ),
            "market_focus": plan.market_focus,
        },
    ) as observation:

        search_service = create_search_service()

        query = (
            f"{state['idea']} "
            f"market size trends industry dynamics "
            f"growth drivers startup opportunity "
            f"{plan.market_focus}"
        )

        search_results = await search_service.search(
            query,
            max_results=5,
        )

        search_context = build_search_context(
            search_results,
        )

        questions = "\n".join(
            f"- {question}"
            for question in plan.market_questions
        )

        user_prompt = f"""
Startup idea:

{state["idea"]}

Market focus:

{plan.market_focus}

Research questions:

{questions}

External research:

{search_context}

Analyze the market opportunity.

Separate:
- evidence-backed claims;
- assumptions;
- opportunities;
- risks;
- evidence gaps.

Use only the supplied research.
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
                    "claim_count": len(
                        result.claims
                    ),
                    "evidence_count": len(
                        result.evidence
                    ),
                    "confidence": result.confidence,
                }
            )

    return {
        "researcher": result,
    }