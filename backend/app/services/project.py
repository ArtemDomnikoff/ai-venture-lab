from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project
from app.repositories.project import ProjectRepository
from app.schemas.project import ProjectCreate, ProjectUpdate


class ProjectService:
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self.session = session
        self.repository = ProjectRepository(session)

    async def create_project(
        self,
        data: ProjectCreate,
        *,
        user_id: uuid.UUID,
    ) -> Project:
        project = await self.repository.create(
            user_id=user_id,
            name=data.name,
            idea=data.idea,
        )

        await self.session.commit()

        return project

    async def get_project(
        self,
        project_id: uuid.UUID,
        *,
        user_id: uuid.UUID,
    ) -> Project | None:
        return await self.repository.get_by_id(
            project_id,
            user_id=user_id,
        )

    async def get_projects(
        self,
        *,
        user_id: uuid.UUID,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Project], int]:
        return await self.repository.get_page(
            user_id=user_id,
            page=page,
            page_size=page_size,
        )

    async def update_project(
        self,
        project_id: uuid.UUID,
        data: ProjectUpdate,
        *,
        user_id: uuid.UUID,
    ) -> Project | None:
        project = await self.repository.get_by_id(
            project_id,
            user_id=user_id,
        )

        if project is None:
            return None

        project = await self.repository.update(
            project,
            name=data.name,
            idea=data.idea,
        )

        await self.session.commit()

        return project

    async def delete_project(
        self,
        project_id: uuid.UUID,
        *,
        user_id: uuid.UUID,
    ) -> bool:
        project = await self.repository.get_by_id(
            project_id,
            user_id=user_id,
        )

        if project is None:
            return False

        await self.repository.delete(project)

        await self.session.commit()

        return True
