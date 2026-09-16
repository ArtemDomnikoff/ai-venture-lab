from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, patch

import pytest

from app.domain.enums import RunStatus
from app.worker.main import process_run


def make_analysis_result() -> dict:
    return {
        "idea": "AI venture evaluator",
        "plan": {
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
        },
        "researcher": {
            "summary": "Research",
            "claims": ["Market claim"],
            "evidence": [],
            "confidence": 80,
        },
        "customer": {
            "summary": "Customer",
            "claims": ["Customer claim"],
            "evidence": [],
            "confidence": 80,
        },
        "competitor": {
            "summary": "Competitor",
            "claims": ["Competitor claim"],
            "evidence": [],
            "confidence": 80,
        },
        "tech": {
            "summary": "Tech",
            "claims": ["Tech claim"],
            "evidence": [],
            "confidence": 80,
        },
        "business": {
            "summary": "Business",
            "claims": ["Business claim"],
            "evidence": [],
            "confidence": 80,
        },
        "skeptic": {
            "summary": "Skeptic",
            "contradictions": [],
            "unsupported_claims": [],
            "risks": ["Risk"],
            "missing_evidence": [],
            "evidence_quality": 80,
        },
        "judge": {
            "score": 80,
            "decision": "promising_but_risky",
            "strengths": ["Strength"],
            "risks": ["Risk"],
            "confidence": 80,
        },
    }


def make_run(
    run_id: uuid.UUID,
    project_id: uuid.UUID,
):
    return type(
        "FakeRun",
        (),
        {
            "id": run_id,
            "project_id": project_id,
            "status": RunStatus.QUEUED,
            "project": type(
                "FakeProject",
                (),
                {
                    "idea": "AI venture evaluator",
                },
            )(),
            "started_at": None,
            "finished_at": None,
            "result": None,
            "error": None,
        },
    )()


@pytest.mark.asyncio
async def test_process_run_completes_run() -> None:
    run_id = uuid.uuid4()
    project_id = uuid.uuid4()

    run = make_run(
        run_id=run_id,
        project_id=project_id,
    )

    session = AsyncMock()

    repository = AsyncMock()
    repository.get_by_id.return_value = run

    analysis_result = make_analysis_result()

    analysis_fn = AsyncMock(
        return_value=analysis_result,
    )

    with patch(
        "app.worker.main.RunRepository",
        return_value=repository,
    ):
        await process_run(
            session=session,
            run_id=run_id,
            analysis_fn=analysis_fn,
        )

    assert run.result == analysis_result
    assert run.error is None
    assert run.started_at is not None
    assert run.finished_at is not None

    repository.get_by_id.assert_awaited_once_with(
        run_id,
    )

    assert repository.update_status.await_count == 2

    first_update = repository.update_status.await_args_list[0]
    second_update = repository.update_status.await_args_list[1]

    assert first_update.args == (
        run,
        RunStatus.RUNNING,
    )

    assert second_update.args == (
        run,
        RunStatus.COMPLETED,
    )

    analysis_fn.assert_awaited_once_with(
        session,
        run_id,
        project_id,
        "AI venture evaluator",
    )

    assert session.commit.await_count == 2


@pytest.mark.asyncio
async def test_process_run_ignores_missing_run() -> None:
    run_id = uuid.uuid4()

    session = AsyncMock()

    repository = AsyncMock()
    repository.get_by_id.return_value = None

    analysis_fn = AsyncMock()

    with patch(
        "app.worker.main.RunRepository",
        return_value=repository,
    ):
        await process_run(
            session=session,
            run_id=run_id,
            analysis_fn=analysis_fn,
        )

    repository.get_by_id.assert_awaited_once_with(
        run_id,
    )

    analysis_fn.assert_not_awaited()
    repository.update_status.assert_not_awaited()
    session.commit.assert_not_awaited()


@pytest.mark.asyncio
async def test_process_run_ignores_non_queued_run() -> None:
    run_id = uuid.uuid4()
    project_id = uuid.uuid4()

    run = make_run(
        run_id=run_id,
        project_id=project_id,
    )

    run.status = RunStatus.RUNNING

    session = AsyncMock()

    repository = AsyncMock()
    repository.get_by_id.return_value = run

    analysis_fn = AsyncMock()

    with patch(
        "app.worker.main.RunRepository",
        return_value=repository,
    ):
        await process_run(
            session=session,
            run_id=run_id,
            analysis_fn=analysis_fn,
        )

    repository.get_by_id.assert_awaited_once_with(
        run_id,
    )

    analysis_fn.assert_not_awaited()
    repository.update_status.assert_not_awaited()
    session.commit.assert_not_awaited()


@pytest.mark.asyncio
async def test_process_run_marks_run_failed_when_analysis_raises() -> None:
    run_id = uuid.uuid4()
    project_id = uuid.uuid4()

    run = make_run(
        run_id=run_id,
        project_id=project_id,
    )

    session = AsyncMock()

    repository = AsyncMock()
    repository.get_by_id.return_value = run

    analysis_fn = AsyncMock(
        side_effect=RuntimeError(
            "analysis failed",
        ),
    )

    with patch(
        "app.worker.main.RunRepository",
        return_value=repository,
    ):
        await process_run(
            session=session,
            run_id=run_id,
            analysis_fn=analysis_fn,
        )

    assert run.error == "analysis failed"
    assert run.finished_at is not None
    assert run.result is None

    assert repository.update_status.await_count == 2

    first_update = repository.update_status.await_args_list[0]
    second_update = repository.update_status.await_args_list[1]

    assert first_update.args == (
        run,
        RunStatus.RUNNING,
    )

    assert second_update.args == (
        run,
        RunStatus.FAILED,
    )

    analysis_fn.assert_awaited_once_with(
        session,
        run_id,
        project_id,
        "AI venture evaluator",
    )

    assert session.commit.await_count == 2