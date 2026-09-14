from __future__ import annotations

import uuid

import pytest
from typing import NoReturn
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.enums import RunStatus
from app.models.project import Project
from app.models.run import Run
from app.worker.main import process_run, parse_run_id


@pytest.mark.asyncio
async def test_process_run_completes_run(
    session: AsyncSession,
) -> None:
    project = Project(
        name="Worker Completion Test",
        idea="Testing successful worker execution.",
    )

    session.add(project)
    await session.flush()

    run = Run(
        project_id=project.id,
        status=RunStatus.QUEUED,
    )

    session.add(run)
    await session.commit()

    await process_run(
        session=session,
        run_id=run.id,
    )

    result = await session.execute(
        select(Run).where(Run.id == run.id)
    )

    updated_run = result.scalar_one()

    assert updated_run.status is RunStatus.COMPLETED
    assert updated_run.result is not None
    assert updated_run.result["message"] == "Mock analysis completed"
    assert updated_run.result["score"] == 50
    assert updated_run.error is None
    assert updated_run.started_at is not None
    assert updated_run.finished_at is not None

async def failing_analysis(
    run_id: uuid.UUID,
) -> NoReturn:
    raise RuntimeError("Mock analysis failed")


@pytest.mark.asyncio
async def test_process_run_marks_failed_on_error(
    session: AsyncSession,
) -> None:
    project = Project(
        name="Worker Failure Test",
        idea="Testing failed worker execution.",
    )

    session.add(project)
    await session.flush()

    run = Run(
        project_id=project.id,
        status=RunStatus.QUEUED,
    )

    session.add(run)
    await session.commit()

    await process_run(
        session=session,
        run_id=run.id,
        analysis_fn=failing_analysis,
    )

    result = await session.execute(
        select(Run).where(Run.id == run.id)
    )

    updated_run = result.scalar_one()

    assert updated_run.status is RunStatus.FAILED
    assert updated_run.error == "Mock analysis failed"
    assert updated_run.result is None
    assert updated_run.started_at is not None
    assert updated_run.finished_at is not None

@pytest.mark.asyncio
async def test_process_run_ignores_non_queued_run(
    session: AsyncSession,
) -> None:
    project = Project(
        name="Worker Status Test",
        idea="Testing worker status guard.",
    )

    session.add(project)
    await session.flush()

    run = Run(
        project_id=project.id,
        status=RunStatus.COMPLETED,
        result={"message": "Already completed"},
    )

    session.add(run)
    await session.commit()

    await process_run(
        session=session,
        run_id=run.id,
    )

    result = await session.execute(
        select(Run).where(Run.id == run.id)
    )

    updated_run = result.scalar_one()

    assert updated_run.status is RunStatus.COMPLETED
    assert updated_run.result == {
        "message": "Already completed",
    }

@pytest.mark.asyncio
async def test_process_run_ignores_missing_run(
    session: AsyncSession,
) -> None:
    run_id = uuid.uuid4()

    await process_run(
        session=session,
        run_id=run_id,
    )

@pytest.mark.asyncio
async def test_process_run_failure_does_not_change_other_run(
    session: AsyncSession,
) -> None:
    project = Project(
        name="Worker Isolation Test",
        idea="Testing isolation between worker runs.",
    )

    session.add(project)
    await session.flush()

    failed_run = Run(
        project_id=project.id,
        status=RunStatus.QUEUED,
    )

    successful_run = Run(
        project_id=project.id,
        status=RunStatus.QUEUED,
    )

    session.add_all(
        [failed_run, successful_run],
    )

    await session.commit()

    await process_run(
        session=session,
        run_id=failed_run.id,
        analysis_fn=failing_analysis,
    )

    await process_run(
        session=session,
        run_id=successful_run.id,
    )

    await session.refresh(failed_run)
    await session.refresh(successful_run)

    assert failed_run.status is RunStatus.FAILED
    assert successful_run.status is RunStatus.COMPLETED

def test_parse_run_id() -> None:
    run_id = uuid.uuid4()

    message = {
        "type": "run_analysis",
        "run_id": str(run_id),
    }

    assert parse_run_id(message) == run_id

def test_parse_run_id_rejects_unknown_message_type() -> None:
    message = {
        "type": "unknown",
        "run_id": str(uuid.uuid4()),
    }

    with pytest.raises(ValueError, match="Unsupported message type"):
        parse_run_id(message)

def test_parse_run_id_requires_run_id() -> None:
    message = {
        "type": "run_analysis",
    }

    with pytest.raises(
        ValueError,
        match="Message does not contain run_id",
    ):
        parse_run_id(message)

def test_parse_run_id_rejects_invalid_uuid() -> None:
    message = {
        "type": "run_analysis",
        "run_id": "not-a-uuid",
    }

    with pytest.raises(ValueError):
        parse_run_id(message)