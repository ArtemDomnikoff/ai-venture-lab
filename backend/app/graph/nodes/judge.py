from __future__ import annotations

from app.graph.schemas import JudgeResult
from app.graph.state import AnalysisState
from app.llm.runner import generate_structured


SYSTEM_PROMPT = """
You are the Judge Agent in a multi-agent startup evaluation system.

Your job is to make the final decision about the startup idea.

You receive:
- Researcher analysis;
- Customer analysis;
- Competitor analysis;
- Tech analysis;
- Business analysis;
- Skeptic's critical review.

Do not perform fresh research.

Base the decision on the supplied analyses and the Skeptic review.

Evaluate:
- attractiveness of the market;
- strength and urgency of the customer problem;
- competitive pressure;
- technical feasibility;
- business model viability;
- quality of evidence;
- contradictions and risks identified by the Skeptic.

Evidence quality must materially affect confidence:
- Strong, relevant evidence increases confidence.
- Weak or indirect evidence decreases confidence.
- Major unsupported claims should reduce the final confidence.
- Contradictory evidence should reduce confidence and may reduce the score.
- Do not treat an unsupported claim as a verified fact.

Possible decisions:
- strong_opportunity
- promising_but_risky
- needs_more_research
- weak_opportunity
- not_recommended

The score must be between 0 and 100.

The final decision must be balanced.
Do not be excessively optimistic or pessimistic.

Return:
- overall score;
- one decision category;
- key strengths;
- key risks;
- confidence.
""".strip()


async def judge_node(state: AnalysisState) -> dict:
    researcher = state["researcher"]
    customer = state["customer"]
    competitor = state["competitor"]
    tech = state["tech"]
    business = state["business"]
    skeptic = state["skeptic"]

    user_prompt = f"""
Startup idea:

{state["idea"]}

=== RESEARCHER ===
{researcher.model_dump_json(indent=2)}

=== CUSTOMER ===
{customer.model_dump_json(indent=2)}

=== COMPETITOR ===
{competitor.model_dump_json(indent=2)}

=== TECH ===
{tech.model_dump_json(indent=2)}

=== BUSINESS ===
{business.model_dump_json(indent=2)}

=== SKEPTIC ===
{skeptic.model_dump_json(indent=2)}

Make the final judgment.

Use the five independent analyses as the primary inputs and
use the Skeptic review to challenge weak reasoning.

Consider:
- What evidence is actually strong?
- Which important claims remain unsupported?
- Are there contradictions?
- Are technical feasibility and business viability consistent?
- Is the customer problem sufficiently compelling?
- Is there a credible competitive position?
- How much uncertainty remains?

Do not perform new research.

Return one of the defined decision categories and explain the
main strengths, risks, and confidence in the decision.
""".strip()

    result = await generate_structured(
        system_prompt=SYSTEM_PROMPT,
        user_prompt=user_prompt,
        output_model=JudgeResult,
    )

    return {
        "judge": result,
    }