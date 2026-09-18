from __future__ import annotations

from app.graph.schemas import JudgeResult
from app.graph.state import AnalysisState
from app.llm.runner import generate_structured
from app.observability import agent_trace

SYSTEM_PROMPT = """
You are the Judge Agent in a multi-agent startup evaluation system.

Your role is to make the final investment-style decision.

You must evaluate the startup idea using ONLY:

- market analysis;
- customer analysis;
- competitor analysis;
- technical analysis;
- business analysis;
- skeptic review.

Evaluate:

- market attractiveness;
- customer demand confidence;
- competitive position;
- technical feasibility;
- business model viability;
- evidence quality;
- overall risk level.

Do not introduce external facts.

Return:

- overall score from 0 to 100;
- final decision;
- strengths;
- risks;
- confidence.

Possible decisions:

- strong_opportunity
- promising_but_risky
- needs_more_research
- weak_opportunity
- not_recommended
""".strip()


async def judge_node(
    state: AnalysisState,
) -> dict:

    with agent_trace(
        agent_name="judge",
        run_id=str(state.get("run_id", "")),
        project_id=str(state.get("project_id", "")),
        idea=state["idea"],
        input_data={
            "evaluation_stage": "final",
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


Skeptic review:

{state["skeptic"].model_dump_json()}


Create the final investment-style evaluation.

Base the decision on:
- evidence quality;
- consistency between analyses;
- identified risks;
- opportunity strength.
""".strip()

        result = await generate_structured(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            output_model=JudgeResult,
        )

        if observation is not None:
            observation.update(
                output={
                    "score": result.score,
                    "decision": result.decision,
                    "confidence": result.confidence,
                }
            )

    return {
        "judge": result,
    }
