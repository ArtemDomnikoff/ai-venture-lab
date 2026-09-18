from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from app.graph.nodes.customer import customer_node
from app.graph.schemas import AgentFinding, Evidence, ResearchPlan
from app.search.models import SearchResult


def make_plan() -> ResearchPlan:
    return ResearchPlan(
        market_questions=["Market?"],
        customer_questions=["Who is the customer?"],
        competition_questions=["Competitors?"],
        tech_questions=["Technology?"],
        business_questions=["Business model?"],
        customer_focus="ICP, pain points, willingness to pay",
        market_focus="Market",
        competition_focus="Competition",
        tech_focus="Technology",
        business_focus="Business",
    )


@pytest.mark.asyncio
async def test_customer_node_returns_structured_finding() -> None:
    expected = AgentFinding(
        summary="Found a clear target segment.",
        claims=["Startup founders are a relevant customer segment."],
        evidence=[
            Evidence(
                claim="Startup founders are a relevant customer segment.",
                source="https://example.com/customers",
                source_type="research",
                excerpt="Founders report this problem.",
                confidence=82,
            )
        ],
        confidence=80,
    )

    search_service = AsyncMock()
    search_service.search.return_value = [
        SearchResult(
            title="Customer research",
            url="https://example.com/customers",
            snippet="Founders report this problem.",
            source="Example",
            score=0.9,
        )
    ]

    with (
        patch(
            "app.graph.nodes.customer.create_search_service",
            return_value=search_service,
        ),
        patch(
            "app.graph.nodes.customer.generate_structured",
            new=AsyncMock(return_value=expected),
        ),
    ):
        result = await customer_node(
            {
                "idea": "AI venture evaluator",
                "plan": make_plan(),
            }
        )

    assert result["customer"] == expected
    assert result["customer"].evidence[0].source == "https://example.com/customers"
