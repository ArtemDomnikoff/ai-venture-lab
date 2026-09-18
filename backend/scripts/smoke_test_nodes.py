from __future__ import annotations

import asyncio
import uuid

from app.graph.nodes.business import business_node
from app.graph.nodes.competitor import competitor_node
from app.graph.nodes.customer import customer_node
from app.graph.nodes.judge import judge_node
from app.graph.nodes.researcher import researcher_node
from app.graph.nodes.skeptic import skeptic_node
from app.graph.nodes.tech import tech_node
from app.graph.schemas import (
    AgentFinding,
    JudgeResult,
    ResearchPlan,
    SkepticResult,
)
from app.graph.state import AnalysisState
from app.observability import (
    analysis_trace,
    get_langfuse,
    is_langfuse_enabled,
)

#
# Fake Tavily
#


class FakeSearchService:
    async def search(
        self,
        query: str,
        max_results: int = 5,
    ):

        return [
            {
                "title": "Fake source",
                "url": "https://example.com/source",
                "content": ("Fake evidence for smoke test."),
            }
        ]


#
# Fake LLM
#


async def fake_generate_structured(
    *,
    system_prompt,
    user_prompt,
    output_model,
    **kwargs,
):

    if output_model is AgentFinding:
        return AgentFinding(
            summary="Mock agent analysis",
            claims=["Mock claim"],
            evidence=[],
            confidence=80,
        )

    if output_model is SkepticResult:
        return SkepticResult(
            summary="Mock skeptic review",
            contradictions=[],
            unsupported_claims=[],
            risks=["Mock risk"],
            missing_evidence=[],
            evidence_quality=80,
        )

    if output_model is JudgeResult:
        return JudgeResult(
            score=75,
            decision="promising_but_risky",
            strengths=["Mock strength"],
            risks=["Mock risk"],
            confidence=80,
        )

    raise RuntimeError(f"Unknown model {output_model}")


async def main():

    if not is_langfuse_enabled():
        raise RuntimeError("Langfuse disabled")

    langfuse = get_langfuse()

    if langfuse is None:
        raise RuntimeError("Langfuse unavailable")

    run_id = str(uuid.uuid4())
    project_id = str(uuid.uuid4())

    state: AnalysisState = {
        "run_id": uuid.UUID(run_id),
        "project_id": uuid.UUID(project_id),
        "idea": ("AI platform for automated startup evaluation"),
        "plan": ResearchPlan(
            market_questions=["Market size?"],
            customer_questions=["Who is customer?"],
            competition_questions=["Who are competitors?"],
            tech_questions=["Technical risks?"],
            business_questions=["Business model?"],
            customer_focus="ICP",
            market_focus="Market",
            competition_focus="Competition",
            tech_focus="Technology",
            business_focus="Business model",
        ),
    }

    #
    # monkey patch
    #

    import app.llm.runner
    import app.search.client

    app.search.client.create_search_service = lambda: FakeSearchService()

    app.llm.runner.generate_structured = fake_generate_structured

    with analysis_trace(
        run_id=run_id,
        project_id=project_id,
        idea=state["idea"],
    ):
        results = await asyncio.gather(
            researcher_node(state),
            customer_node(state),
            competitor_node(state),
            tech_node(state),
            business_node(state),
        )

        for result in results:
            state.update(result)

        skeptic = await skeptic_node(state)

        state.update(skeptic)

        judge = await judge_node(state)

        state.update(judge)

    langfuse.flush()

    print("NODE OBSERVATION SMOKE TEST OK")

    print(state["judge"])


if __name__ == "__main__":
    asyncio.run(main())
