from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.domain.enums import RunStatus
from app.observability_metrics import RunMetricsService


@pytest.mark.asyncio
async def test_get_metrics_returns_status_counts() -> None:
    session = AsyncMock()

    status_result = MagicMock()
    status_result.all.return_value = [
        (RunStatus.QUEUED, 2),
        (RunStatus.RUNNING, 1),
        (RunStatus.COMPLETED, 5),
        (RunStatus.FAILED, 2),
    ]

    duration_result = MagicMock()
    duration_result.scalar_one_or_none.return_value = 1.5

    session.execute.side_effect = [
        status_result,
        duration_result,
    ]

    service = RunMetricsService(session)

    metrics = await service.get_metrics()

    assert metrics.total_runs == 10
    assert metrics.queued_runs == 2
    assert metrics.running_runs == 1
    assert metrics.completed_runs == 5
    assert metrics.failed_runs == 2
    assert metrics.average_duration_ms == 1500.0


@pytest.mark.asyncio
async def test_get_metrics_defaults_missing_statuses_to_zero() -> None:
    session = AsyncMock()

    status_result = MagicMock()
    status_result.all.return_value = [
        (RunStatus.COMPLETED, 3),
    ]

    duration_result = MagicMock()
    duration_result.scalar_one_or_none.return_value = None

    session.execute.side_effect = [
        status_result,
        duration_result,
    ]

    service = RunMetricsService(session)

    metrics = await service.get_metrics()

    assert metrics.total_runs == 3
    assert metrics.queued_runs == 0
    assert metrics.running_runs == 0
    assert metrics.completed_runs == 3
    assert metrics.failed_runs == 0
    assert metrics.average_duration_ms is None


@pytest.mark.asyncio
async def test_get_metrics_handles_no_runs() -> None:
    session = AsyncMock()

    status_result = MagicMock()
    status_result.all.return_value = []

    duration_result = MagicMock()
    duration_result.scalar_one_or_none.return_value = None

    session.execute.side_effect = [
        status_result,
        duration_result,
    ]

    service = RunMetricsService(session)

    metrics = await service.get_metrics()

    assert metrics.total_runs == 0
    assert metrics.queued_runs == 0
    assert metrics.running_runs == 0
    assert metrics.completed_runs == 0
    assert metrics.failed_runs == 0
    assert metrics.average_duration_ms is None


def test_run_metrics_as_dict() -> None:
    from app.observability_metrics import RunMetrics

    metrics = RunMetrics(
        total_runs=10,
        queued_runs=2,
        running_runs=1,
        completed_runs=5,
        failed_runs=2,
        average_duration_ms=1500.0,
    )

    assert metrics.as_dict() == {
        "total_runs": 10,
        "queued_runs": 2,
        "running_runs": 1,
        "completed_runs": 5,
        "failed_runs": 2,
        "average_duration_ms": 1500.0,
    }
