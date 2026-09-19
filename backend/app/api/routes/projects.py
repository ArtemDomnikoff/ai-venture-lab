from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_session
from app.core.exceptions import ProjectNotFoundError
from app.models.user import User
from app.schemas.project import (
    ProjectCreate,
    ProjectListResponse,
    ProjectResponse,
    ProjectUpdate,
)
from app.services.project import ProjectService

router = APIRouter(
    prefix="/projects",
    tags=["projects"],
)


@router.post(
    "",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_project(
    data: ProjectCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ProjectResponse:
    service = ProjectService(session)

    return await service.create_project(
        data,
        user_id=current_user.id,
    )


@router.get(
    "",
    response_model=ProjectListResponse,
    status_code=status.HTTP_200_OK,
)
async def get_projects(
    page: int = Query(
        default=1,
        ge=1,
    ),
    page_size: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ProjectListResponse:
    service = ProjectService(session)

    projects, total = await service.get_projects(
        user_id=current_user.id,
        page=page,
        page_size=page_size,
    )

    return ProjectListResponse(
        items=projects,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/{project_id}",
    response_model=ProjectResponse,
    status_code=status.HTTP_200_OK,
)
async def get_project(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ProjectResponse:
    service = ProjectService(session)

    project = await service.get_project(
        project_id,
        user_id=current_user.id,
    )

    if project is None:
        raise ProjectNotFoundError(
            str(project_id),
        )

    return project


@router.patch(
    "/{project_id}",
    response_model=ProjectResponse,
    status_code=status.HTTP_200_OK,
)
async def update_project(
    project_id: uuid.UUID,
    data: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> ProjectResponse:
    service = ProjectService(session)

    project = await service.update_project(
        project_id,
        data,
        user_id=current_user.id,
    )

    if project is None:
        raise ProjectNotFoundError(
            str(project_id),
        )

    return project


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_project(
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> None:
    service = ProjectService(session)

    deleted = await service.delete_project(
        project_id,
        user_id=current_user.id,
    )

    if not deleted:
        raise ProjectNotFoundError(
            str(project_id),
        )
