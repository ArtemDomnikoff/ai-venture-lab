from __future__ import annotations

from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from app.api.deps import (
    get_current_user,
    get_session,
)
from app.main import app
from app.models.user import User
from app.observability_metrics import RunMetrics


def make_test_user() -> User:
    return User(
        id=uuid4(),
        email="metrics@example.com",
        password_hash="test",
        free_runs_remaining=3,
    )


@pytest.mark.asyncio
async def test_get_run_metrics_returns_metrics() -> None:
    session = AsyncMock()
    user = make_test_user()

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

    async def override_get_current_user() -> User:
        return user

    app.dependency_overrides[get_session] = (
        override_get_session
    )

    app.dependency_overrides[get_current_user] = (
        override_get_current_user
    )

    try:
        with patch(
            "app.api.routes.metrics.RunMetricsService",
        ) as mock_service_class:
            mock_service = (
                mock_service_class.return_value
            )

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
                response = await client.get(
                    "/api/v1/metrics/runs",
                )

        assert response.status_code == 200

        assert response.json() == {
            "total_runs": 10,
            "queued_runs": 2,
            "running_runs": 1,
            "completed_runs": 5,
            "failed_runs": 2,
            "average_duration_ms": 1532.41,
        }

        mock_service.get_metrics.assert_awaited_once_with(
            user_id=user.id,
        )

    finally:
        app.dependency_overrides.pop(
            get_session,
            None,
        )

        app.dependency_overrides.pop(
            get_current_user,
            None,
        )


@pytest.mark.asyncio
async def test_get_run_metrics_returns_null_average_for_no_completed_runs() -> None:
    session = AsyncMock()
    user = make_test_user()

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

    async def override_get_current_user() -> User:
        return user

    app.dependency_overrides[get_session] = (
        override_get_session
    )

    app.dependency_overrides[get_current_user] = (
        override_get_current_user
    )

    try:
        with patch(
            "app.api.routes.metrics.RunMetricsService",
        ) as mock_service_class:
            mock_service = (
                mock_service_class.return_value
            )

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
                response = await client.get(
                    "/api/v1/metrics/runs",
                )

        assert response.status_code == 200

        assert response.json() == {
            "total_runs": 3,
            "queued_runs": 2,
            "running_runs": 1,
            "completed_runs": 0,
            "failed_runs": 0,
            "average_duration_ms": None,
        }

        mock_service.get_metrics.assert_awaited_once_with(
            user_id=user.id,
        )

    finally:
        app.dependency_overrides.pop(
            get_session,
            None,
        )

        app.dependency_overrides.pop(
            get_current_user,
            None,
        )
