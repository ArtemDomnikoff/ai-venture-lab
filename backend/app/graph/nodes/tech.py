from __future__ import annotations

from app.graph.evidence import build_search_context, validate_agent_evidence
from app.graph.schemas import AgentFinding
from app.graph.state import AnalysisState
from app.llm.runner import generate_structured
from app.search.client import create_search_service


SYSTEM_PROMPT = """
You are the Tech Agent in a multi-agent startup evaluation system.

Your job is to independently assess the technical feasibility of the
startup idea.

Focus on:
- architecture;
- required technologies;
- AI/ML requirements;
- data requirements;
- external integrations;
- infrastructure;
- security;
- privacy;
- scalability;
- implementation complexity;
- major technical risks;
- likely build-versus-buy decisions.

You must perform an independent analysis.
Do not rely on the outputs of other agents.

Use the supplied external search results where they provide useful
technical or ecosystem evidence.

Evidence rules:
- Only use evidence from the supplied search sources.
- For every evidence item, source MUST be the exact URL from the search results.
- Do not invent URLs, publications, technologies, benchmarks, or statistics.
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


async def tech_node(state: AnalysisState) -> dict:
    plan = state["plan"]

    search_service = create_search_service()

    query = (
        f"{state['idea']} "
        f"technical architecture feasibility technologies "
        f"integrations security scalability implementation complexity "
        f"{plan.tech_focus}"
    )

    search_results = await search_service.search(
        query,
        max_results=5,
    )

    search_context = build_search_context(search_results)

    questions = "\n".join(
        f"- {question}"
        for question in plan.tech_questions
    )

    user_prompt = f"""
Startup idea:

{state["idea"]}

Technical focus:

{plan.tech_focus}

Research questions:

{questions}

External search results:

{search_context}

Assess technical feasibility and implementation complexity.

Clearly distinguish:
- established technical facts;
- reasonable engineering assumptions;
- uncertain areas that require validation.

Do not invent benchmarks, technology capabilities, or implementation costs.
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
        "tech": result,
    }