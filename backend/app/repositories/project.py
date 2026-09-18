from __future__ import annotations

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project


class ProjectRepository:
    def __init__(
        self,
        session: AsyncSession,
    ):
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

        await self.session.flush()
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

    async def get_page(
        self,
        *,
        page: int,
        page_size: int,
    ) -> tuple[list[Project], int]:
        offset = (page - 1) * page_size

        total_result = await self.session.execute(select(func.count(Project.id)))

        total = total_result.scalar_one()

        result = await self.session.execute(
            select(Project)
            .order_by(
                Project.created_at.desc(),
            )
            .offset(offset)
            .limit(page_size)
        )

        projects = list(result.scalars().all())

        return projects, total

    async def update(
        self,
        project: Project,
        *,
        name: str | None = None,
        idea: str | None = None,
    ) -> Project:
        if name is not None:
            project.name = name

        if idea is not None:
            project.idea = idea

        await self.session.flush()
        await self.session.refresh(project)

        return project

    async def delete(
        self,
        project: Project,
    ) -> None:
        await self.session.delete(project)
