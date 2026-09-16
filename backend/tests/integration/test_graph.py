from __future__ import annotations

import pytest

from app.graph.graph import build_graph
from app.graph.schemas import (
    AgentFinding,
    JudgeResult,
    ResearchPlan,
    SkepticResult,
)


def make_plan() -> ResearchPlan:
    return ResearchPlan(
        market_questions=["Market?"],
        customer_questions=["Customer?"],
        competition_questions=["Competition?"],
        tech_questions=["Tech?"],
        business_questions=["Business?"],
        customer_focus="Customer",
        market_focus="Market",
        competition_focus="Competition",
        tech_focus="Technology",
        business_focus="Business",
    )


def make_finding(name: str) -> AgentFinding:
    return AgentFinding(
        summary=f"{name} summary",
        claims=[f"{name} claim"],
        evidence=[],
        confidence=80,
    )


def make_skeptic() -> SkepticResult:
    return SkepticResult(
        summary="Skeptic summary",
        contradictions=[],
        unsupported_claims=[],
        risks=["Risk"],
        missing_evidence=[],
        evidence_quality=80,
    )


def make_judge() -> JudgeResult:
    return JudgeResult(
        score=80,
        decision="promising_but_risky",
        strengths=["Strength"],
        risks=["Risk"],
        confidence=80,
    )


@pytest.mark.asyncio
async def test_graph_runs_from_start_to_end(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fake_planner(state):
        return {"plan": make_plan()}

    async def fake_researcher(state):
        return {"researcher": make_finding("Researcher")}

    async def fake_customer(state):
        return {"customer": make_finding("Customer")}

    async def fake_competitor(state):
        return {"competitor": make_finding("Competitor")}

    async def fake_tech(state):
        return {"tech": make_finding("Tech")}

    async def fake_business(state):
        return {"business": make_finding("Business")}

    async def fake_skeptic(state):
        return {"skeptic": make_skeptic()}

    async def fake_judge(state):
        return {"judge": make_judge()}

    monkeypatch.setattr(
        "app.graph.graph.planner_node",
        fake_planner,
    )
    monkeypatch.setattr(
        "app.graph.graph.researcher_node",
        fake_researcher,
    )
    monkeypatch.setattr(
        "app.graph.graph.customer_node",
        fake_customer,
    )
    monkeypatch.setattr(
        "app.graph.graph.competitor_node",
        fake_competitor,
    )
    monkeypatch.setattr(
        "app.graph.graph.tech_node",
        fake_tech,
    )
    monkeypatch.setattr(
        "app.graph.graph.business_node",
        fake_business,
    )
    monkeypatch.setattr(
        "app.graph.graph.skeptic_node",
        fake_skeptic,
    )
    monkeypatch.setattr(
        "app.graph.graph.judge_node",
        fake_judge,
    )

    graph = build_graph()

    result = await graph.ainvoke(
        {
            "idea": "AI venture evaluator",
        }
    )

    assert result["idea"] == "AI venture evaluator"
    assert result["plan"] == make_plan()

    assert result["researcher"] == make_finding("Researcher")
    assert result["customer"] == make_finding("Customer")
    assert result["competitor"] == make_finding("Competitor")
    assert result["tech"] == make_finding("Tech")
    assert result["business"] == make_finding("Business")

    assert result["skeptic"] == make_skeptic()
    assert result["judge"] == make_judge()