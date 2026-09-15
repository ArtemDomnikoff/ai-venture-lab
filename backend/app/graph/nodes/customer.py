from __future__ import annotations

from app.graph.evidence import build_search_context, validate_agent_evidence
from app.graph.schemas import AgentFinding
from app.graph.state import AnalysisState
from app.llm.runner import generate_structured
from app.search.client import create_search_service


SYSTEM_PROMPT = """
You are the Customer Agent in a multi-agent startup evaluation system.

Your job is to independently analyze the customer side of the startup idea.

Focus on:
- ideal customer profile;
- customer segments;
- pain points;
- jobs-to-be-done;
- current alternatives;
- buying behavior;
- willingness to pay;
- urgency of the problem;
- adoption barriers.

You must perform an independent analysis.
Do not rely on the outputs of other agents.

Use the supplied external search results as evidence.

Evidence rules:
- Only use evidence from the supplied search sources.
- For every evidence item, source MUST be the exact URL from the search results.
- Do not invent URLs, publications, companies, reports, or statistics.
- If a claim is not supported by the retrieved sources, leave it unsupported
  rather than inventing evidence.
- Evidence confidence reflects how strongly the retrieved source supports
  the claim.

Return:
- a concise summary;
- important claims;
- evidence supporting those claims;
- overall confidence.
""".strip()


async def customer_node(state: AnalysisState) -> dict:
    plan = state["plan"]

    search_service = create_search_service()

    query = (
        f"{state['idea']} "
        f"target customers ICP pain points jobs to be done "
        f"buying behavior willingness to pay customer needs "
        f"{plan.customer_focus}"
    )

    search_results = await search_service.search(
        query,
        max_results=5,
    )

    search_context = build_search_context(search_results)

    questions = "\n".join(
        f"- {question}"
        for question in plan.customer_questions
    )

    user_prompt = f"""
Startup idea:

{state["idea"]}

Customer focus:

{plan.customer_focus}

Research questions:

{questions}

External search results:

{search_context}

Analyze the customer problem and target audience.

Distinguish evidence-backed observations from assumptions.
Do not invent customer statistics or unsupported willingness-to-pay claims.
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

    return {
        "customer": result,
    }