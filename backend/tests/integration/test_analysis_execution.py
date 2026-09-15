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


class FakeAsyncIterator:
    def __init__(self, updates: list[dict]):
        self.updates = updates

    def __aiter__(self):
        return self

    async def __anext__(self):
        if not self.updates:
            raise StopAsyncIteration

        return self.updates.pop(0)


def make_fake_run(
    run_id: uuid.UUID,
    project_id: uuid.UUID,
):
    return SimpleNamespace(
        id=run_id,
        project_id=project_id,
        current_node=None,
        progress={},
    )


def make_fake_updates() -> list[dict]:
    result = make_fake_result()

    return [
        {
            "planner": {
                "plan": result["plan"],
            },
        },
        {
            "researcher": {
                "researcher": result["researcher"],
            },
        },
        {
            "customer": {
                "customer": result["customer"],
            },
        },
        {
            "competitor": {
                "competitor": result["competitor"],
            },
        },
        {
            "tech": {
                "tech": result["tech"],
            },
        },
        {
            "business": {
                "business": result["business"],
            },
        },
        {
            "skeptic": {
                "skeptic": result["skeptic"],
            },
        },
        {
            "judge": {
                "judge": result["judge"],
            },
        },
    ]


@pytest.mark.asyncio
async def test_run_analysis_returns_json_compatible_result() -> None:
    run_id = uuid.uuid4()
    project_id = uuid.uuid4()

    fake_session = AsyncMock()

    fake_run = make_fake_run(
        run_id,
        project_id,
    )

    fake_repository = AsyncMock()
    fake_repository.get_by_id.return_value = fake_run

    fake_graph = SimpleNamespace(
        astream=lambda *args, **kwargs: FakeAsyncIterator(
            make_fake_updates()
        )
    )

    with (
        patch(
            "app.worker.execution.build_graph",
            return_value=fake_graph,
        ),
        patch(
            "app.worker.execution.RunRepository",
            return_value=fake_repository,
        ),
    ):
        result = await run_analysis(
            session=fake_session,
            run_id=run_id,
            project_id=project_id,
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
async def test_run_analysis_passes_correct_state_to_graph() -> None:
    run_id = uuid.uuid4()
    project_id = uuid.uuid4()

    fake_session = AsyncMock()

    fake_run = make_fake_run(
        run_id,
        project_id,
    )

    fake_repository = AsyncMock()
    fake_repository.get_by_id.return_value = fake_run

    captured_args = None
    captured_kwargs = None

    async def fake_astream(*args, **kwargs):
        nonlocal captured_args
        nonlocal captured_kwargs

        captured_args = args
        captured_kwargs = kwargs

        for update in make_fake_updates():
            yield update

    fake_graph = SimpleNamespace(
        astream=fake_astream,
    )

    with (
        patch(
            "app.worker.execution.build_graph",
            return_value=fake_graph,
        ),
        patch(
            "app.worker.execution.RunRepository",
            return_value=fake_repository,
        ),
    ):
        await run_analysis(
            session=fake_session,
            run_id=run_id,
            project_id=project_id,
            idea="AI venture evaluator",
        )

    assert captured_args is not None
    assert captured_kwargs is not None

    input_state = captured_args[0]

    assert input_state["run_id"] == run_id
    assert input_state["project_id"] == project_id
    assert input_state["idea"] == "AI venture evaluator"

    assert captured_kwargs["stream_mode"] == "updates"