from __future__ import annotations

from app.graph.schemas import JudgeNarrative, JudgeResult
from app.graph.scoring import (
    calculate_final_confidence,
    calculate_overall_score,
    decision_for_score,
)
from app.graph.state import AnalysisState
from app.llm.runner import generate_structured
from app.observability import agent_trace

SYSTEM_PROMPT = """
You are the final Judge Agent in a startup evaluation system.

The numerical score has ALREADY been calculated by the backend from the five
domain scores and skeptic penalties.

You must NOT invent, change, round, or override the score.

Your task is to explain the result:
- concise summary;
- strongest evidence-backed strengths;
- most important risks.

Do not introduce external facts.
Do not produce a new numerical score.
Do not give generic praise.
Every strength and risk should be grounded in the supplied analyses.
""".strip()


async def judge_node(
    state: AnalysisState,
) -> dict:
    score, breakdown, risk_penalty = (
        calculate_overall_score(
            state,
        )
    )

    decision = decision_for_score(
        score,
    )

    confidence = calculate_final_confidence(
        state,
    )

    with agent_trace(
        agent_name="judge",
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
            "evaluation_stage": "final",
            "score": score,
            "decision": decision,
            "risk_penalty": risk_penalty,
        },
    ) as observation:
        user_prompt = f"""
Startup idea:

{state["idea"]}

Deterministic domain scores:

Market: {state["researcher"].score}
Customer: {state["customer"].score}
Competition: {state["competitor"].score}
Technology: {state["tech"].score}
Business: {state["business"].score}

Skeptic review:

{state["skeptic"].model_dump_json()}

Score breakdown:

{chr(10).join(
    f"- {item.dimension}: "
    f"score={item.score}, "
    f"weight={item.weight:.0%}, "
    f"contribution={item.contribution}"
    for item in breakdown
)}

Deterministic final score: {score}
Deterministic decision: {decision}
Deterministic risk penalty: {risk_penalty}

Write the final narrative only.
""".strip()

        narrative = await generate_structured(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            output_model=JudgeNarrative,
        )

        result = JudgeResult(
            score=score,
            decision=decision,
            summary=narrative.summary,
            strengths=narrative.strengths,
            risks=narrative.risks,
            confidence=confidence,
            evidence_quality=state[
                "skeptic"
            ].evidence_quality,
            score_breakdown=breakdown,
            risk_penalty=risk_penalty,
        )

        if observation is not None:
            observation.update(
                output={
                    "score": result.score,
                    "decision": result.decision,
                    "confidence": result.confidence,
                    "risk_penalty": result.risk_penalty,
                    "evidence_quality": result.evidence_quality,
                }
            )

        return {
            "judge": result,
        }
