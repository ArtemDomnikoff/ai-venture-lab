from __future__ import annotations

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project


class ProjectRepository:
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self.session = session

    async def create(
        self,
        *,
        user_id: uuid.UUID,
        name: str,
        idea: str,
    ) -> Project:
        project = Project(
            user_id=user_id,
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
        *,
        user_id: uuid.UUID | None = None,
    ) -> Project | None:
        statement = select(Project).where(
            Project.id == project_id,
        )

        if user_id is not None:
            statement = statement.where(
                Project.user_id == user_id,
            )

        result = await self.session.execute(statement)

        return result.scalar_one_or_none()

    async def get_page(
        self,
        *,
        user_id: uuid.UUID,
        page: int,
        page_size: int,
    ) -> tuple[list[Project], int]:
        offset = (page - 1) * page_size

        total_result = await self.session.execute(
            select(func.count(Project.id)).where(
                Project.user_id == user_id,
            )
        )

        total = total_result.scalar_one()

        result = await self.session.execute(
            select(Project)
            .where(
                Project.user_id == user_id,
            )
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
