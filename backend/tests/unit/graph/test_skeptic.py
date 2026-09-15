from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from app.graph.nodes.skeptic import skeptic_node
from app.graph.schemas import AgentFinding, Evidence, SkepticResult


def make_finding(name: str) -> AgentFinding:
    return AgentFinding(
        summary=f"{name} summary",
        claims=[f"{name} claim"],
        evidence=[
            Evidence(
                claim=f"{name} claim",
                source=f"https://example.com/{name.lower()}",
                source_type="research",
                excerpt=f"{name} evidence",
                confidence=80,
            )
        ],
        confidence=80,
    )


@pytest.mark.asyncio
async def test_skeptic_reviews_all_five_agents() -> None:
    expected = SkepticResult(
        summary="Several assumptions require validation.",
        contradictions=[
            "Business assumptions are more optimistic than customer evidence."
        ],
        unsupported_claims=[
            "Willingness to pay is not directly supported."
        ],
        risks=[
            "Customer validation is still required.",
        ],
        missing_evidence=[
            "Direct pricing validation",
        ],
        evidence_quality=72,
    )

    mock_generate = AsyncMock(return_value=expected)

    with patch(
        "app.graph.nodes.skeptic.generate_structured",
        new=mock_generate,
    ):
        result = await skeptic_node(
            {
                "idea": "AI venture evaluator",
                "researcher": make_finding("Researcher"),
                "customer": make_finding("Customer"),
                "competitor": make_finding("Competitor"),
                "tech": make_finding("Tech"),
                "business": make_finding("Business"),
            }
        )

    assert result["skeptic"] == expected

    kwargs = mock_generate.await_args.kwargs
    prompt = kwargs["user_prompt"]

    assert "=== RESEARCHER ===" in prompt
    assert "=== CUSTOMER ===" in prompt
    assert "=== COMPETITOR ===" in prompt
    assert "=== TECH ===" in prompt
    assert "=== BUSINESS ===" in prompt

    assert "https://example.com/researcher" in prompt
    assert "https://example.com/customer" in prompt
    assert "https://example.com/competitor" in prompt
    assert "https://example.com/tech" in prompt
    assert "https://example.com/business" in prompt