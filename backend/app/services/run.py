from __future__ import annotations

import uuid

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    ProjectNotFoundError,
    RunAlreadyRunningError,
)
from app.models.run import Run
from app.queue.base import Queue
from app.repositories.project import ProjectRepository
from app.repositories.run import RunRepository


class RunService:
    def __init__(
        self,
        session: AsyncSession,
        queue: Queue | None = None,
    ):
        self.session = session
        self.queue = queue

        self.project_repository = ProjectRepository(
            session,
        )
        self.run_repository = RunRepository(
            session,
        )

    async def create_run(
        self,
        project_id: uuid.UUID,
    ) -> Run:
        if self.queue is None:
            raise RuntimeError(
                "Queue is required to create a run",
            )

        project = await self.project_repository.get_by_id(
            project_id,
        )

        if project is None:
            raise ProjectNotFoundError(
                str(project_id),
            )

        active_run = await self.run_repository.get_active_by_project_id(
            project_id,
        )

        if active_run is not None:
            raise RunAlreadyRunningError(
                str(project_id),
            )

        try:
            run = await self.run_repository.create(
                project_id=project_id,
            )

            await self.session.commit()

        except IntegrityError as exc:
            await self.session.rollback()

            raise RunAlreadyRunningError(
                str(project_id),
            ) from exc

        await self.queue.enqueue_run(
            run.id,
        )

        return run

    async def get_run(
        self,
        run_id: uuid.UUID,
    ) -> Run | None:
        return await self.run_repository.get_by_id(
            run_id,
        )

    async def get_project_runs(
        self,
        project_id: uuid.UUID,
        *,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Run], int]:
        project = await self.project_repository.get_by_id(
            project_id,
        )

        if project is None:
            raise ProjectNotFoundError(
                str(project_id),
            )

        return await self.run_repository.get_project_page(
            project_id=project_id,
            page=page,
            page_size=page_size,
        )