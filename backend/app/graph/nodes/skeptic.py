from __future__ import annotations

from app.graph.schemas import SkepticResult
from app.graph.state import AnalysisState
from app.llm.runner import generate_structured


SYSTEM_PROMPT = """
You are the Skeptic Agent in a multi-agent startup evaluation system.

Your job is to critically review the independent analyses produced by
five specialized agents:
- Researcher
- Customer
- Competitor
- Tech
- Business

Do not perform a fresh independent analysis.

Instead, critically compare the five analyses and look for:
- contradictions between agents;
- unsupported or weakly supported claims;
- assumptions presented as facts;
- overly optimistic conclusions;
- inconsistencies between technical feasibility and business economics;
- inconsistencies between customer needs and competitive positioning;
- missing evidence;
- important risks ignored by the other agents.

Be adversarial but fair.

Do not reject claims merely because they are uncertain.
Distinguish uncertainty from actual contradiction.

Evidence assessment:
- Check whether important claims are actually supported by their cited evidence.
- Treat a claim without evidence as weaker than an evidence-supported claim.
- Treat irrelevant evidence as weak support.
- Treat weak, indirect, or low-quality sources cautiously.
- Check whether the cited source actually relates to the claim.
- A URL alone does not prove a claim.
- Pay attention to claims where the evidence only partially supports the conclusion.
- Identify contradictory evidence when present.
- Do not invent new sources or evidence.

Evaluate the evidence quality across all five analyses.

Return:
- a concise critique summary;
- contradictions;
- unsupported claims;
- important risks;
- missing evidence;
- an overall evidence quality score from 0 to 100.
""".strip()


async def skeptic_node(state: AnalysisState) -> dict:
    researcher = state["researcher"]
    customer = state["customer"]
    competitor = state["competitor"]
    tech = state["tech"]
    business = state["business"]

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

Critically compare these five analyses.

For each important conclusion, consider:
1. What exactly is being claimed?
2. Is there evidence supporting it?
3. Does the evidence actually support the claim?
4. Is the evidence direct or indirect?
5. Are there contradictions with another agent?
6. What important evidence is missing?

Pay particular attention to:
- market claims without evidence;
- customer claims without evidence;
- competitor claims based on weak information;
- technical claims presented with unjustified certainty;
- pricing and business assumptions without support;
- conflicts between what customers supposedly want and what competitors offer;
- conflicts between technical feasibility and business economics.

Do not perform fresh research.
Review only the supplied analyses and their evidence.
""".strip()

    result = await generate_structured(
        system_prompt=SYSTEM_PROMPT,
        user_prompt=user_prompt,
        output_model=SkepticResult,
    )

    return {
        "skeptic": result,
    }