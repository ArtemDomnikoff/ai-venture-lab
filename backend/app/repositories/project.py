import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project


class ProjectRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        *,
        name: str,
        idea: str,
    ) -> Project:
        project = Project(
            name=name,
            idea=idea,
        )

        self.session.add(project)

        await self.session.commit()
        await self.session.refresh(project)

        return project

    async def get_by_id(
        self,
        project_id: uuid.UUID,
    ) -> Project | None:
        result = await self.session.execute(
            select(Project).where(
                Project.id == project_id,
            )
        )

        return result.scalar_one_or_none()

    async def get_all(self) -> list[Project]:
        result = await self.session.execute(
            select(Project).order_by(
                Project.created_at.desc(),
            )
        )

        return list(result.scalars().all())

    async def delete(
        self,
        project: Project,
    ) -> None:
        await self.session.delete(project)
        await self.session.commit()