from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_session
from app.models.user import User
from app.schemas.result import (
    AnalysisResultResponse,
    DetailedAnalysisResultResponse,
    FindingResponse,
)
from app.services.result import ResultService

router = APIRouter(prefix="/runs", tags=["results"])


@router.get("/{run_id}/result", response_model=AnalysisResultResponse)
async def get_result(
    run_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> AnalysisResultResponse:
    service = ResultService(session)
    return await service.get_result(run_id, user_id=current_user.id)


@router.get("/{run_id}/result/detail", response_model=DetailedAnalysisResultResponse)
async def get_detailed_result(
    run_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> DetailedAnalysisResultResponse:
    service = ResultService(session)
    return await service.get_detailed_result(run_id, user_id=current_user.id)


@router.get("/{run_id}/findings", response_model=list[FindingResponse])
async def get_findings(
    run_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> list[FindingResponse]:
    service = ResultService(session)
    return await service.get_findings(run_id, user_id=current_user.id)
