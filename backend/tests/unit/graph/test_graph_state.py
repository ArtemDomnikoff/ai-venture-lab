from __future__ import annotations

import uuid

from app.graph.schemas import AgentFinding, ResearchPlan
from app.graph.state import AnalysisState


def test_analysis_state_accepts_initial_graph_input() -> None:
    run_id = uuid.uuid4()
    project_id = uuid.uuid4()

    state: AnalysisState = {
        "run_id": run_id,
        "project_id": project_id,
        "idea": "AI startup evaluation platform",
    }

    assert state["run_id"] == run_id
    assert state["project_id"] == project_id
    assert state["idea"] == "AI startup evaluation platform"


def test_analysis_state_accepts_plan_and_agent_results() -> None:
    plan = ResearchPlan(
        market_questions=["Market size?"],
        customer_questions=["Who is the customer?"],
        competition_questions=["Who are the competitors?"],
        tech_questions=["Is it technically feasible?"],
        business_questions=["How can it make money?"],
        customer_focus="ICP",
        market_focus="Market",
        competition_focus="Competition",
        tech_focus="Technology",
        business_focus="Business model",
    )

    finding = AgentFinding(
        summary="Summary",
        claims=["Claim"],
        evidence=[],
        confidence=80,
    )

    state: AnalysisState = {
        "idea": "AI startup evaluator",
        "plan": plan,
        "researcher": finding,
        "customer": finding,
        "competitor": finding,
        "tech": finding,
        "business": finding,
    }

    assert state["plan"] == plan
    assert state["researcher"] == finding
    assert state["customer"] == finding
    assert state["competitor"] == finding
    assert state["tech"] == finding
    assert state["business"] == finding
