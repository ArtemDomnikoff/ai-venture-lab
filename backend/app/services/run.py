import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ProjectNotFoundError
from app.models.run import Run
from app.domain.enums import ProjectStatus
from app.repositories.project import ProjectRepository
from app.repositories.run import RunRepository


class RunService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.project_repository = ProjectRepository(session)
        self.run_repository = RunRepository(session)

    async def create_run(
        self,
        project_id: uuid.UUID,
    ) -> Run:
        project = await self.project_repository.get_by_id(project_id)

        if project is None:
            raise ProjectNotFoundError(
                f"Project {project_id} not found"
            )

        run = await self.run_repository.create(
            project_id=project_id,
        )

        await self.session.commit()

        return run

    async def get_run(
        self,
        run_id: uuid.UUID,
    ) -> Run | None:
        return await self.run_repository.get_by_id(run_id)

    async def get_project_runs(
        self,
        project_id: uuid.UUID,
    ) -> list[Run]:
        project = await self.project_repository.get_by_id(project_id)

        if project is None:
            raise ProjectNotFoundError(
                f"Project {project_id} not found"
            )

        return await self.run_repository.get_by_project_id(project_id)