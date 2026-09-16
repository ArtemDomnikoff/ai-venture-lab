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
You are the Competitor Agent in a multi-agent startup evaluation system.

Your job is to analyze the competitive landscape.

Focus on:
- direct competitors;
- indirect competitors;
- substitutes;
- market positioning;
- differentiation opportunities;
- competitive risks.

Perform an independent analysis.

Use only supplied search evidence.

Evidence rules:
- Use only URLs returned by search.
- Do not invent competitors, companies, reports, statistics, or market facts.
- Separate evidence-backed observations from assumptions.

Return:
- summary;
- claims;
- evidence;
- risks;
- opportunities;
- confidence.
""".strip()


async def competitor_node(
    state: AnalysisState,
) -> dict:

    plan = state["plan"]

    with agent_trace(
        agent_name="competitor",
        run_id=str(
            state.get("run_id", "")
        ),
        project_id=str(
            state.get("project_id", "")
        ),
        idea=state["idea"],
        input_data={
            "question_count": len(
                plan.competition_questions
            ),
            "competition_focus": (
                plan.competition_focus
            ),
        },
    ) as observation:

        search_service = create_search_service()

        query = (
            f"{state['idea']} "
            f"competitors alternatives "
            f"market landscape differentiation "
            f"competitive risks "
            f"{plan.competition_focus}"
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
            for question in plan.competition_questions
        )

        user_prompt = f"""
Startup idea:

{state["idea"]}

Competition focus:

{plan.competition_focus}

Research questions:

{questions}

External research:

{search_context}

Analyze the competitive environment.

Identify:
- direct competitors;
- indirect competitors;
- substitutes;
- differentiation opportunities;
- competitive risks.

Separate evidence-backed findings from assumptions.
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
        "competitor": result,
    }