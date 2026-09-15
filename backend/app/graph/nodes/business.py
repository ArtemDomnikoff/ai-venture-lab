from __future__ import annotations

from app.graph.evidence import build_search_context, validate_agent_evidence
from app.graph.schemas import AgentFinding
from app.graph.state import AnalysisState
from app.llm.runner import generate_structured
from app.search.client import create_search_service


SYSTEM_PROMPT = """
You are the Business Agent in a multi-agent startup evaluation system.

Your job is to independently assess the business model and economic
potential of the startup idea.

Focus on:
- business model;
- pricing;
- monetization;
- revenue streams;
- customer acquisition;
- CAC considerations;
- margins;
- retention;
- scalability;
- operational costs;
- unit economics;
- economic risks.

You must perform an independent analysis.
Do not rely on the outputs of other agents.

Use the supplied external search results as evidence where relevant.

Evidence rules:
- Only use evidence from the supplied search sources.
- For every evidence item, source MUST be the exact URL from the search results.
- Do not invent URLs, publications, companies, prices, or financial statistics.
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


async def business_node(state: AnalysisState) -> dict:
    plan = state["plan"]

    search_service = create_search_service()

    query = (
        f"{state['idea']} "
        f"business model pricing monetization unit economics "
        f"customer acquisition CAC margins scalability revenue "
        f"{plan.business_focus}"
    )

    search_results = await search_service.search(
        query,
        max_results=5,
    )

    search_context = build_search_context(search_results)

    questions = "\n".join(
        f"- {question}"
        for question in plan.business_questions
    )

    user_prompt = f"""
Startup idea:

{state["idea"]}

Business focus:

{plan.business_focus}

Research questions:

{questions}

External search results:

{search_context}

Analyze the business model and economic potential.

Pay special attention to:
- how the company could make money;
- what customers might pay for;
- acquisition economics;
- scalability;
- major economic assumptions.

Do not invent financial metrics or unsupported pricing benchmarks.
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
        "business": result,
    }