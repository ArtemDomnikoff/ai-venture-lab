from __future__ import annotations

from pydantic import BaseModel, Field


class RunMetricsResponse(BaseModel):
    total_runs: int = Field(
        ge=0,
        description="Total number of runs.",
    )
    queued_runs: int = Field(
        ge=0,
        description="Number of queued runs.",
    )
    running_runs: int = Field(
        ge=0,
        description="Number of currently running runs.",
    )
    completed_runs: int = Field(
        ge=0,
        description="Number of completed runs.",
    )
    failed_runs: int = Field(
        ge=0,
        description="Number of failed runs.",
    )
    average_duration_ms: float | None = Field(
        default=None,
        ge=0,
        description="Average completed run duration in milliseconds.",
    )