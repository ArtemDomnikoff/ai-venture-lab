from __future__ import annotations

from app.graph.schemas import (
    AgentFinding,
    Evidence,
    JudgeResult,
    ResearchPlan,
    SkepticResult,
)


def test_research_plan_accepts_valid_data() -> None:
    plan = ResearchPlan(
        market_questions=["What is the market size?"],
        customer_questions=["Who is the target customer?"],
        competition_questions=["Who are the main competitors?"],
        tech_questions=["What technology is required?"],
        business_questions=["What business model is viable?"],
        customer_focus="ICP, pain points, willingness to pay",
        market_focus="Market size, growth, trends",
        competition_focus="Competitors, pricing, positioning",
        tech_focus="Architecture, feasibility, scalability",
        business_focus="Monetization, pricing, unit economics",
    )

    assert plan.market_questions == ["What is the market size?"]
    assert plan.customer_questions == ["Who is the target customer?"]
    assert plan.competition_questions == ["Who are the main competitors?"]
    assert plan.tech_questions == ["What technology is required?"]
    assert plan.business_questions == ["What business model is viable?"]

    assert plan.market_focus == "Market size, growth, trends"
    assert plan.customer_focus == "ICP, pain points, willingness to pay"
    assert plan.competition_focus == "Competitors, pricing, positioning"
    assert plan.tech_focus == "Architecture, feasibility, scalability"
    assert plan.business_focus == "Monetization, pricing, unit economics"


def test_evidence_accepts_valid_data() -> None:
    evidence = Evidence(
        claim="The market is growing.",
        source="https://example.com/report",
        source_type="industry_report",
        excerpt="The market grew significantly.",
        confidence=90,
    )

    assert evidence.claim == "The market is growing."
    assert evidence.source == "https://example.com/report"
    assert evidence.source_type == "industry_report"
    assert evidence.excerpt == "The market grew significantly."
    assert evidence.confidence == 90


def test_agent_finding_accepts_empty_evidence() -> None:
    finding = AgentFinding(
        summary="The opportunity appears promising.",
        claims=["Demand appears to be growing."],
        evidence=[],
        confidence=75,
    )

    assert finding.evidence == []


def test_agent_finding_accepts_evidence() -> None:
    finding = AgentFinding(
        summary="The opportunity appears promising.",
        claims=["Demand appears to be growing."],
        evidence=[
            Evidence(
                claim="Demand appears to be growing.",
                source="https://example.com/report",
                source_type="industry_report",
                excerpt="Demand grew during the reported period.",
                confidence=85,
            )
        ],
        confidence=80,
    )

    assert len(finding.evidence) == 1


def test_skeptic_result_accepts_evidence_quality() -> None:
    result = SkepticResult(
        summary="The analyses contain several assumptions.",
        contradictions=[],
        unsupported_claims=["Pricing assumptions are weakly supported."],
        risks=["Customer willingness to pay remains uncertain."],
        missing_evidence=["Pricing validation"],
        evidence_quality=65,
    )

    assert result.evidence_quality == 65
    assert result.risks == ["Customer willingness to pay remains uncertain."]


def test_judge_result_accepts_valid_data() -> None:
    result = JudgeResult(
        score=78,
        decision="promising_but_risky",
        strengths=["Clear customer problem."],
        risks=["Pricing remains uncertain."],
        confidence=72,
    )

    assert result.score == 78
    assert result.decision == "promising_but_risky"
    assert result.confidence == 72
