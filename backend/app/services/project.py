import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project
from app.repositories.project import ProjectRepository
from app.schemas.project import ProjectCreate


class ProjectService:
    def __init__(self, session: AsyncSession):
        self.repository = ProjectRepository(session)

    async def create_project(
        self,
        data: ProjectCreate,
    ) -> Project:
        return await self.repository.create(
            name=data.name,
            idea=data.idea,
        )

    async def get_project(
        self,
        project_id: uuid.UUID,
    ) -> Project | None:
        return await self.repository.get_by_id(project_id)

    async def get_projects(self) -> list[Project]:
        return await self.repository.get_all()

    async def delete_project(
        self,
        project_id: uuid.UUID,
    ) -> bool:
        project = await self.repository.get_by_id(project_id)

        if project is None:
            return False

        await self.repository.delete(project)

        return True