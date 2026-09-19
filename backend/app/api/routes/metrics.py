from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import (
    get_current_user,
    get_session,
)
from app.models.user import User
from app.observability_metrics import RunMetricsService
from app.schemas.observability import RunMetricsResponse

router = APIRouter(
    prefix="/metrics",
    tags=["metrics"],
)


@router.get(
    "/runs",
    response_model=RunMetricsResponse,
)
async def get_run_metrics(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> RunMetricsResponse:
    service = RunMetricsService(session)

    metrics = await service.get_metrics(
        user_id=current_user.id,
    )

    return RunMetricsResponse(
        **metrics.as_dict(),
    )
