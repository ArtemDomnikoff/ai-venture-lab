from __future__ import annotations

from app.graph.schemas import SkepticResult
from app.graph.state import AnalysisState
from app.llm.runner import generate_structured
from app.observability import agent_trace

SYSTEM_PROMPT = """
You are the Skeptic Agent in a multi-agent startup evaluation system.

Your job is to audit five completed domain analyses.

Review:
- whether important claims are actually supported by cited evidence;
- contradictions between domains;
- unsupported assumptions;
- evidence gaps;
- inflated or weakly supported dimension scores;
- risks that could materially change the overall assessment.

Do not introduce outside facts.
Do not perform a new market analysis.
Do not reward generic language.

A good audit is specific:
- identify the exact claim or dimension;
- explain why the support is weak, missing, or contradictory;
- distinguish a real contradiction from a missing fact.

Return:
- summary;
- contradictions;
- unsupported_claims;
- risks;
- missing_evidence;
- score_issues;
- evidence_quality from 0 to 100.
""".strip()


async def skeptic_node(
    state: AnalysisState,
) -> dict:
    with agent_trace(
        agent_name="skeptic",
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
            "review_targets": 5,
        },
    ) as observation:
        user_prompt = f"""
Startup idea:

{state["idea"]}

Market analysis:
{state["researcher"].model_dump_json()}

Customer analysis:
{state["customer"].model_dump_json()}

Competition analysis:
{state["competitor"].model_dump_json()}

Technical analysis:
{state["tech"].model_dump_json()}

Business analysis:
{state["business"].model_dump_json()}

Audit the analyses.

For each material weakness, prefer a concrete statement such as:
"willingness_to_pay score is high, but no evidence source directly supports
pricing or buyer willingness to pay."

Do not introduce facts that are not present in these analyses.
""".strip()

        result = await generate_structured(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            output_model=SkepticResult,
        )

        if observation is not None:
            observation.update(
                output={
                    "risk_count": len(
                        result.risks,
                    ),
                    "contradiction_count": len(
                        result.contradictions,
                    ),
                    "unsupported_count": len(
                        result.unsupported_claims,
                    ),
                    "score_issue_count": len(
                        result.score_issues,
                    ),
                    "evidence_quality": result.evidence_quality,
                }
            )

        return {
            "skeptic": result,
        }
