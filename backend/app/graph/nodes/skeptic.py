from __future__ import annotations

from app.graph.schemas import SkepticResult
from app.graph.state import AnalysisState
from app.llm.runner import generate_structured
from app.observability import agent_trace

SYSTEM_PROMPT = """
You are the Skeptic Agent in a multi-agent startup evaluation system.

Your role is not to create another analysis.

Your job is to audit the quality of the existing research.

Review:

- market analysis;
- customer analysis;
- competitor analysis;
- technical analysis;
- business analysis.

Look for:

- contradictions between agents;
- unsupported claims;
- weak or missing evidence;
- unrealistic assumptions;
- hidden risks;
- areas requiring more research.

Do not introduce external facts.
Evaluate only the provided analyses.

Return:
- summary;
- contradictions;
- unsupported claims;
- risks;
- missing evidence;
- evidence quality score.
""".strip()


async def skeptic_node(
    state: AnalysisState,
) -> dict:

    with agent_trace(
        agent_name="skeptic",
        run_id=str(state.get("run_id", "")),
        project_id=str(state.get("project_id", "")),
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


Audit these analyses.

Identify:

1. Contradictions between findings.
2. Unsupported claims.
3. Missing evidence.
4. Major risks.
5. Weak assumptions.

Do not create a new startup evaluation.
""".strip()

        result = await generate_structured(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            output_model=SkepticResult,
        )

        if observation is not None:
            observation.update(
                output={
                    "risk_count": len(result.risks),
                    "contradiction_count": len(result.contradictions),
                    "evidence_quality": (result.evidence_quality),
                }
            )

    return {
        "skeptic": result,
    }
