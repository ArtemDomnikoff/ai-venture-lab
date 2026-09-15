from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.enums import RunStatus
from app.models.run import Run


class RunRepository:
    def __init__(
        self,
        session: AsyncSession,
    ):
        self.session = session

    async def create(
        self,
        *,
        project_id: uuid.UUID,
    ) -> Run:
        run = Run(
            project_id=project_id,
            status=RunStatus.QUEUED,
            progress={},
            current_node=None,
        )

        self.session.add(run)

        await self.session.flush()
        await self.session.refresh(run)

        return run

    async def get_by_id(
        self,
        run_id: uuid.UUID,
    ) -> Run | None:
        result = await self.session.execute(
            select(Run)
            .options(
                selectinload(Run.project),
            )
            .where(
                Run.id == run_id,
            )
        )

        return result.scalar_one_or_none()

    async def get_by_project_id(
        self,
        project_id: uuid.UUID,
    ) -> list[Run]:
        result = await self.session.execute(
            select(Run)
            .where(
                Run.project_id == project_id,
            )
            .order_by(
                Run.created_at.desc(),
            )
        )

        return list(
            result.scalars().all()
        )

    async def update_status(
        self,
        run: Run,
        status: RunStatus,
    ) -> Run:
        run.status = status

        await self.session.flush()
        await self.session.refresh(run)

        return run

    async def update_progress(
        self,
        run: Run,
        *,
        progress: dict[str, str],
        current_node: str | None = None,
    ) -> Run:
        run.progress = dict(progress)
        run.current_node = current_node

        await self.session.flush()
        await self.session.refresh(run)

        return run