from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.api.deps import get_session
from app.main import app
from app.observability_metrics import RunMetrics


@pytest.mark.asyncio
async def test_get_run_metrics_returns_metrics() -> None:
    session = AsyncMock()

    metrics = RunMetrics(
        total_runs=10,
        queued_runs=2,
        running_runs=1,
        completed_runs=5,
        failed_runs=2,
        average_duration_ms=1532.41,
    )

    async def override_get_session():
        yield session

    app.dependency_overrides[get_session] = override_get_session

    try:
        with patch("app.api.routes.metrics.RunMetricsService") as mock_service_class:
            mock_service = mock_service_class.return_value
            mock_service.get_metrics = AsyncMock(
                return_value=metrics,
            )

            transport = ASGITransport(
                app=app,
            )

            async with AsyncClient(
                transport=transport,
                base_url="http://test",
            ) as client:
                response = await client.get("/api/v1/metrics/runs")

        assert response.status_code == 200

        assert response.json() == {
            "total_runs": 10,
            "queued_runs": 2,
            "running_runs": 1,
            "completed_runs": 5,
            "failed_runs": 2,
            "average_duration_ms": 1532.41,
        }

        mock_service.get_metrics.assert_awaited_once()

    finally:
        app.dependency_overrides.pop(
            get_session,
            None,
        )


@pytest.mark.asyncio
async def test_get_run_metrics_returns_null_average_for_no_completed_runs() -> None:
    session = AsyncMock()

    metrics = RunMetrics(
        total_runs=3,
        queued_runs=2,
        running_runs=1,
        completed_runs=0,
        failed_runs=0,
        average_duration_ms=None,
    )

    async def override_get_session():
        yield session

    app.dependency_overrides[get_session] = override_get_session

    try:
        with patch("app.api.routes.metrics.RunMetricsService") as mock_service_class:
            mock_service = mock_service_class.return_value
            mock_service.get_metrics = AsyncMock(
                return_value=metrics,
            )

            transport = ASGITransport(
                app=app,
            )

            async with AsyncClient(
                transport=transport,
                base_url="http://test",
            ) as client:
                response = await client.get("/api/v1/metrics/runs")

        assert response.status_code == 200

        assert response.json() == {
            "total_runs": 3,
            "queued_runs": 2,
            "running_runs": 1,
            "completed_runs": 0,
            "failed_runs": 0,
            "average_duration_ms": None,
        }

    finally:
        app.dependency_overrides.pop(
            get_session,
            None,
        )
