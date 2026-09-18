from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_queue, get_session
from app.core.exceptions import RunNotFoundError
from app.queue.base import Queue
from app.schemas.run import RunListResponse, RunResponse
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
    queue: Queue = Depends(get_queue),
) -> RunResponse:
    service = RunService(
        session=session,
        queue=queue,
    )

    return await service.create_run(project_id)


@projects_router.get(
    "/{project_id}/runs",
    response_model=RunListResponse,
    status_code=status.HTTP_200_OK,
)
async def get_project_runs(
    project_id: uuid.UUID,
    page: int = Query(
        default=1,
        ge=1,
    ),
    page_size: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    session: AsyncSession = Depends(get_session),
) -> RunListResponse:
    service = RunService(session)

    runs, total = await service.get_project_runs(
        project_id,
        page=page,
        page_size=page_size,
    )

    return RunListResponse(
        items=runs,
        total=total,
        page=page,
        page_size=page_size,
    )


@runs_router.get(
    "/{run_id}",
    response_model=RunResponse,
    status_code=status.HTTP_200_OK,
)
async def get_run(
    run_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
) -> RunResponse:
    service = RunService(session)

    run = await service.get_run(run_id)

    if run is None:
        raise RunNotFoundError(
            str(run_id),
        )

    return run


@runs_router.delete(
    "/{run_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_run(
    run_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
) -> None:

    service = RunService(session)

    deleted = await service.delete_run(
        run_id,
    )

    if not deleted:
        raise RunNotFoundError(
            str(run_id),
        )
