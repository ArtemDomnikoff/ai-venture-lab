from __future__ import annotations

import uuid
from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class AnalysisDecision(StrEnum):
    STRONG_OPPORTUNITY = "strong_opportunity"
    PROMISING_BUT_RISKY = "promising_but_risky"
    NEEDS_MORE_RESEARCH = "needs_more_research"
    WEAK_OPPORTUNITY = "weak_opportunity"
    NOT_RECOMMENDED = "not_recommended"


class FindingCategory(StrEnum):
    MARKET = "market"
    CUSTOMER = "customer"
    COMPETITION = "competition"
    TECHNOLOGY = "technology"
    BUSINESS = "business"
    SKEPTIC = "skeptic"


class AnalysisResultResponse(BaseModel):
    run_id: uuid.UUID

    score: int = Field(
        ge=0,
        le=100,
    )

    decision: AnalysisDecision

    summary: str = Field(
        min_length=1,
    )

    created_at: datetime


class FindingResponse(BaseModel):
    id: uuid.UUID

    category: FindingCategory

    title: str = Field(
        min_length=1,
    )

    summary: str = Field(
        min_length=1,
    )

    confidence: int = Field(
        ge=0,
        le=100,
    )
