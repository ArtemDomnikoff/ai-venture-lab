from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from app.graph.nodes.business import business_node
from app.graph.schemas import AgentFinding, Evidence, ResearchPlan
from app.search.models import SearchResult


def make_plan() -> ResearchPlan:
    return ResearchPlan(
        market_questions=["Market?"],
        customer_questions=["Customer?"],
        competition_questions=["Competitors?"],
        tech_questions=["Technology?"],
        business_questions=["What business model is viable?"],
        customer_focus="Customer",
        market_focus="Market",
        competition_focus="Competition",
        tech_focus="Technology",
        business_focus="Pricing, monetization, unit economics",
    )


@pytest.mark.asyncio
async def test_business_returns_structured_finding() -> None:
    expected = AgentFinding(
        summary="A subscription model looks viable.",
        claims=["A recurring subscription could support the business."],
        evidence=[
            Evidence(
                claim="A recurring subscription could support the business.",
                source="https://example.com/pricing",
                source_type="industry_report",
                excerpt="Comparable products use recurring pricing.",
                confidence=80,
            )
        ],
        confidence=78,
    )

    search_service = AsyncMock()
    search_service.search.return_value = [
        SearchResult(
            title="Pricing research",
            url="https://example.com/pricing",
            snippet="Comparable products use recurring pricing.",
            source="Example",
            score=0.9,
        )
    ]

    with (
        patch(
            "app.graph.nodes.business.create_search_service",
            return_value=search_service,
        ),
        patch(
            "app.graph.nodes.business.generate_structured",
            new=AsyncMock(return_value=expected),
        ),
    ):
        result = await business_node(
            {
                "idea": "AI venture evaluator",
                "plan": make_plan(),
            }
        )

    assert result["business"] == expected
    assert result["business"].evidence[0].source == "https://example.com/pricing"