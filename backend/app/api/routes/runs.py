from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_session
from app.core.exceptions import ProjectNotFoundError
from app.schemas.run import RunResponse
from app.services.run import RunService


projects_router = APIRouter(
    prefix="/projects",
    tags=["runs"],
)

runs_router = APIRouter(
    prefix="/runs",
    tags=["runs"],
)


@projects_router.post(
    "/{project_id}/runs",
    response_model=RunResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_run(
    project_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
) -> RunResponse:
    service = RunService(session)

    try:
        run = await service.create_run(project_id)
    except ProjectNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        ) from exc

    return run


@projects_router.get(
    "/{project_id}/runs",
    response_model=list[RunResponse],
)
async def get_project_runs(
    project_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
) -> list[RunResponse]:
    service = RunService(session)

    try:
        runs = await service.get_project_runs(project_id)
    except ProjectNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        ) from exc

    return runs


@runs_router.get(
    "/{run_id}",
    response_model=RunResponse,
)
async def get_run(
    run_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
) -> RunResponse:
    service = RunService(session)

    run = await service.get_run(run_id)

    if run is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Run not found",
        )

    return run