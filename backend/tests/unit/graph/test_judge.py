from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from app.graph.nodes.judge import judge_node
from app.graph.schemas import (
    AgentFinding,
    Evidence,
    JudgeResult,
    SkepticResult,
)


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


def make_skeptic() -> SkepticResult:
    return SkepticResult(
        summary="Some assumptions remain weak.",
        contradictions=[
            "Business assumptions are more optimistic than customer evidence."
        ],
        unsupported_claims=[
            "Pricing assumption",
        ],
        risks=[
            "Customer willingness to pay",
        ],
        missing_evidence=[
            "Pricing validation",
        ],
        evidence_quality=70,
    )


@pytest.mark.asyncio
async def test_judge_uses_all_agent_results_and_skeptic() -> None:
    expected = JudgeResult(
        score=78,
        decision="promising_but_risky",
        strengths=["Clear problem"],
        risks=["Pricing uncertainty"],
        confidence=74,
    )

    mock_generate = AsyncMock(return_value=expected)

    with patch(
        "app.graph.nodes.judge.generate_structured",
        new=mock_generate,
    ):
        result = await judge_node(
            {
                "idea": "AI venture evaluator",
                "researcher": make_finding("Researcher"),
                "customer": make_finding("Customer"),
                "competitor": make_finding("Competitor"),
                "tech": make_finding("Tech"),
                "business": make_finding("Business"),
                "skeptic": make_skeptic(),
            }
        )

    assert result["judge"] == expected

    kwargs = mock_generate.await_args.kwargs
    prompt = kwargs["user_prompt"]

    assert "=== RESEARCHER ===" in prompt
    assert "=== CUSTOMER ===" in prompt
    assert "=== COMPETITOR ===" in prompt
    assert "=== TECH ===" in prompt
    assert "=== BUSINESS ===" in prompt
    assert "=== SKEPTIC ===" in prompt

    assert '"evidence_quality": 70' in prompt
    assert "Pricing validation" in prompt
    assert "Customer willingness to pay" in prompt