from uuid import uuid4

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.enums import RunStatus
from app.models.project import Project
from app.models.run import Run


@pytest.mark.asyncio
async def test_delete_project_cascades_runs(
    session: AsyncSession,
) -> None:
    project = Project(
        name="Cascade Test",
        idea="Testing cascade deletion of project runs.",
    )

    session.add(project)
    await session.flush()

    run = Run(
        project_id=project.id,
        status=RunStatus.QUEUED,
    )

    session.add(run)
    await session.commit()

    await session.delete(project)
    await session.commit()

    result = await session.execute(select(Run).where(Run.id == run.id))

    assert result.scalar_one_or_none() is None


@pytest.mark.asyncio
async def test_run_status_is_persisted(
    session: AsyncSession,
) -> None:
    project = Project(
        name="Run Status Test",
        idea="Testing persistence of run status enum.",
    )

    session.add(project)
    await session.flush()

    run = Run(
        project_id=project.id,
        status=RunStatus.QUEUED,
    )

    session.add(run)
    await session.commit()

    result = await session.execute(select(Run).where(Run.id == run.id))

    saved_run = result.scalar_one()

    assert saved_run.status is RunStatus.QUEUED


@pytest.mark.asyncio
async def test_run_requires_existing_project(
    session: AsyncSession,
) -> None:
    run = Run(
        project_id=uuid4(),
        status=RunStatus.QUEUED,
    )

    session.add(run)

    with pytest.raises(IntegrityError):
        await session.commit()

    await session.rollback()
