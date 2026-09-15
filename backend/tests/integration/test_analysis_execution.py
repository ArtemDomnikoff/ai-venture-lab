from __future__ import annotations

import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest

from app.worker.execution import run_analysis


def make_fake_result() -> dict:
    return {
        "idea": "AI venture evaluator",
        "plan": SimpleNamespace(
            model_dump=lambda: {
                "market_questions": ["Market?"],
                "customer_questions": ["Customer?"],
                "competition_questions": ["Competition?"],
                "tech_questions": ["Technology?"],
                "business_questions": ["Business?"],
                "customer_focus": "Customer",
                "market_focus": "Market",
                "competition_focus": "Competition",
                "tech_focus": "Technology",
                "business_focus": "Business",
            }
        ),
        "researcher": SimpleNamespace(
            model_dump=lambda: {
                "summary": "Research",
                "claims": ["Claim"],
                "evidence": [],
                "confidence": 80,
            }
        ),
        "customer": SimpleNamespace(
            model_dump=lambda: {
                "summary": "Customer",
                "claims": ["Claim"],
                "evidence": [],
                "confidence": 80,
            }
        ),
        "competitor": SimpleNamespace(
            model_dump=lambda: {
                "summary": "Competitor",
                "claims": ["Claim"],
                "evidence": [],
                "confidence": 80,
            }
        ),
        "tech": SimpleNamespace(
            model_dump=lambda: {
                "summary": "Tech",
                "claims": ["Claim"],
                "evidence": [],
                "confidence": 80,
            }
        ),
        "business": SimpleNamespace(
            model_dump=lambda: {
                "summary": "Business",
                "claims": ["Claim"],
                "evidence": [],
                "confidence": 80,
            }
        ),
        "skeptic": SimpleNamespace(
            model_dump=lambda: {
                "summary": "Skeptic",
                "contradictions": [],
                "unsupported_claims": [],
                "risks": ["Risk"],
                "missing_evidence": [],
                "evidence_quality": 80,
            }
        ),
        "judge": SimpleNamespace(
            model_dump=lambda: {
                "score": 80,
                "decision": "promising_but_risky",
                "strengths": ["Strength"],
                "risks": ["Risk"],
                "confidence": 80,
            }
        ),
    }


@pytest.mark.asyncio
async def test_run_analysis_returns_json_compatible_result() -> None:
    fake_graph = AsyncMock()
    fake_graph.ainvoke.return_value = make_fake_result()

    with patch(
        "app.worker.execution.build_graph",
        return_value=fake_graph,
    ):
        result = await run_analysis(
            run_id=uuid.uuid4(),
            project_id=uuid.uuid4(),
            idea="AI venture evaluator",
        )

    assert result["idea"] == "AI venture evaluator"

    assert set(result) == {
        "idea",
        "plan",
        "researcher",
        "customer",
        "competitor",
        "tech",
        "business",
        "skeptic",
        "judge",
    }

    assert isinstance(result["plan"], dict)
    assert isinstance(result["researcher"], dict)
    assert isinstance(result["customer"], dict)
    assert isinstance(result["competitor"], dict)
    assert isinstance(result["tech"], dict)
    assert isinstance(result["business"], dict)
    assert isinstance(result["skeptic"], dict)
    assert isinstance(result["judge"], dict)


@pytest.mark.asyncio
async def test_run_analysis_passes_correct_models_to_agents() -> None:
    fake_graph = AsyncMock()
    fake_graph.ainvoke.return_value = make_fake_result()

    run_id = uuid.uuid4()
    project_id = uuid.uuid4()

    with patch(
        "app.worker.execution.build_graph",
        return_value=fake_graph,
    ):
        await run_analysis(
            run_id=run_id,
            project_id=project_id,
            idea="AI venture evaluator",
        )

    fake_graph.ainvoke.assert_awaited_once()

    input_state = fake_graph.ainvoke.await_args.args[0]

    assert input_state["run_id"] == run_id
    assert input_state["project_id"] == project_id
    assert input_state["idea"] == "AI venture evaluator"