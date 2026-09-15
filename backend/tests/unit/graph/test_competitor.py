from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from app.graph.nodes.competitor import competitor_node
from app.graph.schemas import AgentFinding, Evidence, ResearchPlan
from app.search.models import SearchResult


def make_plan() -> ResearchPlan:
    return ResearchPlan(
        market_questions=["Market?"],
        customer_questions=["Customer?"],
        competition_questions=["Who are the main competitors?"],
        tech_questions=["Technology?"],
        business_questions=["Business model?"],
        customer_focus="Customer",
        market_focus="Market",
        competition_focus="Competitors, pricing, positioning",
        tech_focus="Technology",
        business_focus="Business",
    )


@pytest.mark.asyncio
async def test_competitor_returns_structured_finding() -> None:
    expected = AgentFinding(
        summary="The market has several competitors.",
        claims=["Several established competitors exist."],
        evidence=[
            Evidence(
                claim="Several established competitors exist.",
                source="https://example.com/competitors",
                source_type="company_website",
                excerpt="Competitive products are available.",
                confidence=88,
            )
        ],
        confidence=82,
    )

    search_service = AsyncMock()
    search_service.search.return_value = [
        SearchResult(
            title="Competitive landscape",
            url="https://example.com/competitors",
            snippet="Competitive products are available.",
            source="Example",
            score=0.92,
        )
    ]

    with (
        patch(
            "app.graph.nodes.competitor.create_search_service",
            return_value=search_service,
        ),
        patch(
            "app.graph.nodes.competitor.generate_structured",
            new=AsyncMock(return_value=expected),
        ),
    ):
        result = await competitor_node(
            {
                "idea": "AI venture evaluator",
                "plan": make_plan(),
            }
        )

    assert result["competitor"] == expected
    assert len(result["competitor"].evidence) == 1