from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Any

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.enums import RunStatus
from app.models.project import Project
from app.models.run import Run


@dataclass(frozen=True)
class RunMetrics:
    total_runs: int
    queued_runs: int
    running_runs: int
    completed_runs: int
    failed_runs: int
    average_duration_ms: float | None

    def as_dict(self) -> dict[str, Any]:
        return {
            "total_runs": self.total_runs,
            "queued_runs": self.queued_runs,
            "running_runs": self.running_runs,
            "completed_runs": self.completed_runs,
            "failed_runs": self.failed_runs,
            "average_duration_ms": self.average_duration_ms,
        }


class RunMetricsService:
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self.session = session

    async def get_metrics(
        self,
        *,
        user_id: uuid.UUID | None = None,
    ) -> RunMetrics:
        status_counts = await self._get_status_counts(
            user_id=user_id,
        )

        average_duration_ms = (
            await self._get_average_duration_ms(
                user_id=user_id,
            )
        )

        return RunMetrics(
            total_runs=sum(status_counts.values()),
            queued_runs=status_counts[RunStatus.QUEUED],
            running_runs=status_counts[RunStatus.RUNNING],
            completed_runs=status_counts[RunStatus.COMPLETED],
            failed_runs=status_counts[RunStatus.FAILED],
            average_duration_ms=average_duration_ms,
        )

    async def _get_status_counts(
        self,
        *,
        user_id: uuid.UUID | None,
    ) -> dict[RunStatus, int]:
        statement = select(
            Run.status,
            func.count(Run.id),
        )

        if user_id is not None:
            statement = (
                statement
                .join(
                    Project,
                    Project.id == Run.project_id,
                )
                .where(
                    Project.user_id == user_id,
                )
            )

        statement = statement.group_by(
            Run.status,
        )

        result = await self.session.execute(
            statement,
        )

        counts = {
            status: 0
            for status in RunStatus
        }

        for run_status, count in result.all():
            counts[run_status] = int(count)

        return counts

    async def _get_average_duration_ms(
        self,
        *,
        user_id: uuid.UUID | None,
    ) -> float | None:
        duration_seconds = func.extract(
            "epoch",
            Run.finished_at - Run.started_at,
        )

        statement = select(
            func.avg(
                case(
                    (
                        (Run.started_at.is_not(None))
                        & (Run.finished_at.is_not(None)),
                        duration_seconds,
                    ),
                    else_=None,
                )
            )
        )

        if user_id is not None:
            statement = (
                statement
                .select_from(Run)
                .join(
                    Project,
                    Project.id == Run.project_id,
                )
                .where(
                    Project.user_id == user_id,
                )
            )

        result = await self.session.execute(
            statement,
        )

        average_seconds = (
            result.scalar_one_or_none()
        )

        if average_seconds is None:
            return None

        return round(
            float(average_seconds) * 1000,
            2,
        )
