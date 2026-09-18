from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from app.graph.nodes.tech import tech_node
from app.graph.schemas import AgentFinding, Evidence, ResearchPlan
from app.search.models import SearchResult


def make_plan() -> ResearchPlan:
    return ResearchPlan(
        market_questions=["Market?"],
        customer_questions=["Customer?"],
        competition_questions=["Competitors?"],
        tech_questions=["What technology is required?"],
        business_questions=["Business model?"],
        customer_focus="Customer",
        market_focus="Market",
        competition_focus="Competition",
        tech_focus="Architecture, feasibility, scalability",
        business_focus="Business",
    )


@pytest.mark.asyncio
async def test_tech_node_returns_structured_finding() -> None:
    expected = AgentFinding(
        summary="The product is technically feasible.",
        claims=["A standard cloud architecture is sufficient."],
        evidence=[
            Evidence(
                claim="A standard cloud architecture is sufficient.",
                source="https://example.com/architecture",
                source_type="technical_documentation",
                excerpt="The required stack supports the workload.",
                confidence=84,
            )
        ],
        confidence=86,
    )

    search_service = AsyncMock()
    search_service.search.return_value = [
        SearchResult(
            title="Technical architecture",
            url="https://example.com/architecture",
            snippet="The required stack supports the workload.",
            source="Example",
            score=0.88,
        )
    ]

    with (
        patch(
            "app.graph.nodes.tech.create_search_service",
            return_value=search_service,
        ),
        patch(
            "app.graph.nodes.tech.generate_structured",
            new=AsyncMock(return_value=expected),
        ),
    ):
        result = await tech_node(
            {
                "idea": "AI venture evaluator",
                "plan": make_plan(),
            }
        )

    assert result["tech"] == expected
    assert result["tech"].confidence == 86
