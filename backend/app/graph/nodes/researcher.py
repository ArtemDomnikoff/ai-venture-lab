from __future__ import annotations

from app.graph.evidence import build_search_context, validate_agent_evidence
from app.graph.schemas import AgentFinding
from app.graph.state import AnalysisState
from app.llm.runner import generate_structured
from app.search.client import create_search_service


SYSTEM_PROMPT = """
You are the Researcher Agent in a multi-agent startup evaluation system.

Your job is to independently research the market and problem space
for the startup idea.

Focus on:
- market size and growth;
- market trends;
- problem prevalence;
- industry dynamics;
- relevant regulations or structural changes;
- important signals that could affect the opportunity.

You must perform an independent analysis.
Do not rely on or reference the outputs of other agents.

Use the supplied external search results as evidence.

Do not invent:
- sources;
- URLs;
- publications;
- statistics;
- market sizes;
- companies;
- trends.

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


async def researcher_node(state: AnalysisState) -> dict:
    plan = state["plan"]

    search_service = create_search_service()

    query = (
        f"{state['idea']} "
        f"market size market growth trends industry problem validation "
        f"{plan.market_focus}"
    )

    search_results = await search_service.search(
        query,
        max_results=5,
    )

    search_context = build_search_context(search_results)

    questions = "\n".join(
        f"- {question}"
        for question in plan.market_questions
    )

    user_prompt = f"""
Startup idea:

{state["idea"]}

Research focus:

{plan.market_focus}

Research questions:

{questions}

External search results:

{search_context}

Analyze the market and problem space using the retrieved sources.

Separate:
- facts supported by evidence;
- reasonable interpretation;
- uncertainty.

Do not invent unsupported statistics or sources.
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
        "researcher": result,
    }