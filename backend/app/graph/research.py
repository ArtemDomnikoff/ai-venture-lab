from __future__ import annotations

from app.graph.evidence import (
    build_search_context,
    validate_agent_evidence,
)
from app.graph.schemas import AgentFinding, ResearchDraft
from app.graph.scoring import (
    calculate_agent_confidence,
    calculate_agent_score,
    scoring_instructions,
)
from app.graph.state import AnalysisState
from app.llm.runner import generate_structured
from app.observability import agent_trace
from app.search.client import create_search_service
from app.search.models import SearchResult

DOMAIN_CONTEXT = {
    "researcher": """
Investigate market demand, market size, growth, market structure, access to
the market, and concrete category-level demand signals.

Prefer primary or authoritative sources for market size and statistics.
Look for dates, percentages, named segments, geographic scope, and methodology.
""",
    "customer": """
Investigate the actual customer problem, ICP, pain intensity, frequency,
willingness to pay, buying behavior, and adoption barriers.

Look for actual pricing, buyer language, reviews, surveys, procurement behavior,
job postings, communities, and other direct demand signals.
""",
    "competitor": """
Investigate direct competitors, indirect competitors, substitutes, prices,
product positioning, feature gaps, customer complaints, switching costs, and
defensibility.

Prefer concrete competitor facts over generic market summaries.
""",
    "tech": """
Investigate technical feasibility, required infrastructure, implementation
complexity, technical constraints, scaling considerations, and realistic
time-to-MVP.

Prefer official documentation, technical papers, benchmarks, and credible
engineering sources.
""",
    "business": """
Investigate monetization, pricing, cost drivers, unit economics, distribution,
sales motion, and scalability.

Look for actual competitor pricing, SaaS benchmarks, market pricing behavior,
and concrete cost or distribution evidence.
""",
}


def _questions_text(
    questions: list[str],
) -> str:
    return "\n".join(
        f"- {question}"
        for question in questions
    )


def _dedupe_queries(
    queries: list[str],
) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []

    for query in queries:
        value = " ".join(
            query.split(),
        ).strip()

        if not value:
            continue

        key = value.casefold()

        if key in seen:
            continue

        seen.add(key)

        result.append(
            value,
        )

    return result


async def run_research_agent(
    state: AnalysisState,
    *,
    agent_key: str,
    questions: list[str],
    queries: list[str],
    focus: str,
) -> AgentFinding:
    with agent_trace(
        agent_name=agent_key,
        run_id=str(
            state.get(
                "run_id",
                "",
            )
        ),
        project_id=str(
            state.get(
                "project_id",
                "",
            )
        ),
        idea=state["idea"],
        input_data={
            "question_count": len(
                questions,
            ),
            "query_count": len(
                queries,
            ),
            "focus": focus,
        },
    ) as observation:
        search_service = create_search_service()

        initial_results = await search_service.search_many(
            queries[:4],
            max_results_per_query=5,
            max_total_results=12,
        )

        initial_context = build_search_context(
            initial_results,
        )

        draft_system_prompt = f"""
You are the research discovery phase of the {agent_key} agent in a startup
analysis system.

Your job is to inspect the initial search evidence, identify what is actually
known, and identify the most important unanswered questions.

{DOMAIN_CONTEXT[agent_key]}

Do not invent facts.
Do not write a generic overview.
Prefer concrete, falsifiable findings.

Return:
- key_findings;
- evidence_gaps;
- up to 3 targeted follow-up search queries.

The follow-up queries must directly address material gaps in the supplied
research and must not simply repeat the original queries.
""".strip()

        draft_user_prompt = f"""
Startup idea:

{state["idea"]}

Research focus:

{focus}

Research questions:

{_questions_text(questions)}

Initial search evidence:

{initial_context}
""".strip()

        draft = await generate_structured(
            system_prompt=draft_system_prompt,
            user_prompt=draft_user_prompt,
            output_model=ResearchDraft,
        )

        follow_up_queries = _dedupe_queries(
            draft.follow_up_queries,
        )[:2]

        follow_up_results: list[SearchResult] = []

        if follow_up_queries:
            follow_up_results = await search_service.search_many(
                follow_up_queries,
                max_results_per_query=5,
                max_total_results=8,
            )

        all_results = search_service.merge_results(
            initial_results,
            follow_up_results,
            max_total_results=14,
        )

        final_context = build_search_context(
            all_results,
        )

        final_system_prompt = f"""
You are the {agent_key} research agent in an AI startup evaluation system.

You are given a concrete research plan and retrieved web evidence.

{DOMAIN_CONTEXT[agent_key]}

Your job is to produce an evidence-grounded domain assessment.

{scoring_instructions(agent_key)}

Output requirements:
- claims must be concrete and decision-useful;
- strengths and opportunities must be evidence-backed;
- risks must be specific and material;
- prefer numbers, dates, prices, named companies, named technologies, and
  explicit market facts when available;
- explicitly state when reliable evidence is missing;
- separate evidence-backed claims from inference;
- do not repeat a generic startup description;
- use [SOURCE n] references in dimension score evidence_sources;
- never invent URLs or facts.
""".strip()

        final_user_prompt = f"""
Startup idea:

{state["idea"]}

Research focus:

{focus}

Research questions:

{_questions_text(questions)}

Initial discovery findings:

{chr(10).join(
    f"- {item}"
    for item in draft.key_findings
)}

Identified evidence gaps:

{
    chr(10).join(
        f"- {item}"
        for item in draft.evidence_gaps
    )
    if draft.evidence_gaps
    else "- No explicit evidence gaps identified in the discovery pass."
}

Final retrieved evidence:

{final_context}

Produce the final {agent_key} assessment.

Important:
- Answer the research questions using the evidence.
- Do not treat missing evidence as positive evidence.
- Do not turn generic plausibility into a high score.
- Use exactly five rubric dimensions.
- Every dimension rationale should explain why the evidence leads to the score.
""".strip()

        result = await generate_structured(
            system_prompt=final_system_prompt,
            user_prompt=final_user_prompt,
            output_model=AgentFinding,
        )

        result = validate_agent_evidence(
            result,
            all_results,
        )

        result = calculate_agent_score(
            result,
            agent_key,
            all_results,
        )

        result = calculate_agent_confidence(
            result,
            all_results,
        )

        if observation is not None:
            observation.update(
                output={
                    "query_count": len(
                        queries[:4],
                    ),
                    "follow_up_query_count": len(
                        follow_up_queries,
                    ),
                    "result_count": len(
                        all_results,
                    ),
                    "claim_count": len(
                        result.claims,
                    ),
                    "evidence_count": len(
                        result.evidence,
                    ),
                    "score": result.score,
                    "confidence": result.confidence,
                    "dimension_scores": {
                        item.dimension: item.score
                        for item in result.dimension_scores
                    },
                }
            )

        return result
