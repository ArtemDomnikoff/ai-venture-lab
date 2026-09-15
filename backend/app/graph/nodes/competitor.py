from __future__ import annotations

from app.graph.evidence import build_search_context, validate_agent_evidence
from app.graph.schemas import AgentFinding
from app.graph.state import AnalysisState
from app.llm.runner import generate_structured
from app.search.client import create_search_service


SYSTEM_PROMPT = """
You are the Competitor Agent in a multi-agent startup evaluation system.

Your job is to independently analyze the competitive landscape
for the startup idea.

Focus on:
- direct competitors;
- indirect competitors;
- substitute solutions;
- competitor positioning;
- pricing;
- target customers;
- strengths and weaknesses;
- market saturation;
- possible differentiation.

You must perform an independent analysis.
Do not rely on the outputs of other agents.

Use the supplied external search results as evidence.

Evidence rules:
- Only use evidence from the supplied search sources.
- For every evidence item, source MUST be the exact URL from the search results.
- Do not invent URLs, publications, companies, reports, prices, or statistics.
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


async def competitor_node(state: AnalysisState) -> dict:
    plan = state["plan"]

    search_service = create_search_service()

    query = (
        f"{state['idea']} "
        f"competitors alternatives substitutes pricing positioning "
        f"competitive landscape differentiation "
        f"{plan.competition_focus}"
    )

    search_results = await search_service.search(
        query,
        max_results=5,
    )

    search_context = build_search_context(search_results)

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

External search results:

{search_context}

Analyze the competitive landscape.

Identify direct and indirect alternatives and explain
where differentiation may or may not exist.

Do not invent competitors, pricing, market shares, or product capabilities.
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
        "competitor": result,
    }