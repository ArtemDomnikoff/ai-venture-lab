from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from app.graph.nodes.researcher import researcher_node
from app.graph.schemas import AgentFinding, Evidence, ResearchPlan
from app.search.models import SearchResult


def make_plan() -> ResearchPlan:
    return ResearchPlan(
        market_questions=["What is the market size?"],
        customer_questions=["Who is the target customer?"],
        competition_questions=["Who are the main competitors?"],
        tech_questions=["What technology is required?"],
        business_questions=["What business model is viable?"],
        customer_focus="ICP",
        market_focus="Market size and trends",
        competition_focus="Competitors",
        tech_focus="Architecture",
        business_focus="Monetization",
    )


def make_search_results() -> list[SearchResult]:
    return [
        SearchResult(
            title="Market report",
            url="https://example.com/market",
            snippet="Market demand is growing.",
            source="Example Research",
            score=0.95,
        )
    ]


@pytest.mark.asyncio
async def test_researcher_returns_structured_finding() -> None:
    expected = AgentFinding(
        summary="The market appears attractive.",
        claims=["Market demand is growing."],
        evidence=[
            Evidence(
                claim="Market demand is growing.",
                source="https://example.com/market",
                source_type="industry_report",
                excerpt="Market demand is growing.",
                confidence=90,
            )
        ],
        confidence=85,
    )

    search_service = AsyncMock()
    search_service.search.return_value = make_search_results()

    with (
        patch(
            "app.graph.nodes.researcher.create_search_service",
            return_value=search_service,
        ),
        patch(
            "app.graph.nodes.researcher.generate_structured",
            new=AsyncMock(return_value=expected),
        ),
    ):
        result = await researcher_node(
            {
                "idea": "AI venture evaluator",
                "plan": make_plan(),
            }
        )

    assert result["researcher"] == expected
    assert len(result["researcher"].evidence) == 1


@pytest.mark.asyncio
async def test_researcher_removes_unretrieved_evidence() -> None:
    expected = AgentFinding(
        summary="Summary",
        claims=["Claim"],
        evidence=[
            Evidence(
                claim="Claim",
                source="https://not-found.example/report",
                source_type="web",
                excerpt="Unsupported.",
                confidence=95,
            )
        ],
        confidence=80,
    )

    search_service = AsyncMock()
    search_service.search.return_value = make_search_results()

    with (
        patch(
            "app.graph.nodes.researcher.create_search_service",
            return_value=search_service,
        ),
        patch(
            "app.graph.nodes.researcher.generate_structured",
            new=AsyncMock(return_value=expected),
        ),
    ):
        result = await researcher_node(
            {
                "idea": "AI venture evaluator",
                "plan": make_plan(),
            }
        )

    assert result["researcher"].evidence == []