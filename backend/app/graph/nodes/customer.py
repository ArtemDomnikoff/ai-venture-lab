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
You are the Customer Agent in a multi-agent startup evaluation system.

Your job is to analyze customer demand.

Focus on:
- target customers;
- ideal customer profile (ICP);
- customer pain points;
- willingness to pay;
- adoption barriers;
- buying behavior.

Perform an independent analysis.

Use only supplied search evidence.

Evidence rules:
- Use only URLs returned by search.
- Do not invent customers, surveys, statistics, companies, or market facts.
- Separate evidence-backed observations from assumptions.

Return:
- summary;
- claims;
- evidence;
- risks;
- opportunities;
- confidence.
""".strip()


async def customer_node(
    state: AnalysisState,
) -> dict:

    plan = state["plan"]

    with agent_trace(
        agent_name="customer",
        run_id=str(state.get("run_id", "")),
        project_id=str(state.get("project_id", "")),
        idea=state["idea"],
        input_data={
            "question_count": len(plan.customer_questions),
            "customer_focus": plan.customer_focus,
        },
    ) as observation:
        search_service = create_search_service()

        query = (
            f"{state['idea']} "
            f"customer ICP users pain points "
            f"willingness to pay adoption barriers "
            f"{plan.customer_focus}"
        )

        search_results = await search_service.search(
            query,
            max_results=5,
        )

        search_context = build_search_context(
            search_results,
        )

        questions = "\n".join(f"- {question}" for question in plan.customer_questions)

        user_prompt = f"""
Startup idea:

{state["idea"]}

Customer focus:

{plan.customer_focus}

Research questions:

{questions}

External research:

{search_context}

Analyze:
- who the customers are;
- their problems;
- willingness to pay;
- adoption risks.

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
                    "claim_count": len(result.claims),
                    "evidence_count": len(result.evidence),
                    "confidence": result.confidence,
                }
            )

    return {
        "customer": result,
    }
