from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from app.graph.nodes.planner import planner_node
from app.graph.schemas import ResearchPlan


@pytest.mark.asyncio
async def test_planner_node_returns_structured_plan() -> None:
    expected_plan = ResearchPlan(
        market_questions=["What is the market size?"],
        customer_questions=["Who is the target customer?"],
        competition_questions=["Who are the main competitors?"],
        tech_questions=["What technology is required?"],
        business_questions=["What business model is viable?"],
        customer_focus="ICP and willingness to pay",
        market_focus="Market size and growth",
        competition_focus="Competitors and positioning",
        tech_focus="Architecture and feasibility",
        business_focus="Pricing and unit economics",
    )

    with patch(
        "app.graph.nodes.planner.generate_structured",
        new=AsyncMock(return_value=expected_plan),
    ):
        result = await planner_node(
            {
                "idea": "AI startup idea evaluator",
            }
        )

    assert result["plan"] == expected_plan


@pytest.mark.asyncio
async def test_planner_node_calls_llm_with_startup_idea() -> None:
    expected_plan = ResearchPlan(
        market_questions=["Market size?"],
        customer_questions=["Customer?"],
        competition_questions=["Competitors?"],
        tech_questions=["Technology?"],
        business_questions=["Business model?"],
        customer_focus="Customers",
        market_focus="Market",
        competition_focus="Competition",
        tech_focus="Tech",
        business_focus="Business",
    )

    mock_generate = AsyncMock(return_value=expected_plan)

    with patch(
        "app.graph.nodes.planner.generate_structured",
        new=mock_generate,
    ):
        await planner_node(
            {
                "idea": "AI venture evaluator",
            }
        )

    assert mock_generate.await_count == 1

    kwargs = mock_generate.await_args.kwargs

    assert "AI venture evaluator" in kwargs["user_prompt"]
    assert kwargs["output_model"] is ResearchPlan
