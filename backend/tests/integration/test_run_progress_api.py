from __future__ import annotations

import uuid
from datetime import UTC, datetime
from types import SimpleNamespace

import pytest
from httpx import ASGITransport, AsyncClient

from app.api.deps import (
    get_current_user,
    get_session,
)
from app.domain.enums import RunStatus
from app.main import app
from app.models.run import Run


class FakeSession:
    pass


def make_run(
    *,
    run_id: uuid.UUID | None = None,
    project_id: uuid.UUID | None = None,
) -> Run:
    return Run(
        id=run_id or uuid.uuid4(),
        project_id=project_id or uuid.uuid4(),
        status=RunStatus.RUNNING,
        progress={
            "planner": "completed",
            "researcher": "running",
            "customer": "completed",
            "competitor": "waiting",
            "tech": "waiting",
            "business": "waiting",
            "skeptic": "waiting",
            "judge": "waiting",
        },
        current_node=None,
        started_at=datetime.now(UTC),
        finished_at=None,
        result=None,
        error=None,
        created_at=datetime.now(UTC),
    )


@pytest.mark.asyncio
async def test_get_run_returns_progress(
    monkeypatch,
) -> None:
    run_id = uuid.uuid4()
    project_id = uuid.uuid4()
    user_id = uuid.uuid4()

    run = make_run(
        run_id=run_id,
        project_id=project_id,
    )

    fake_user = SimpleNamespace(
        id=user_id,
    )

    class FakeRunService:
        def __init__(
            self,
            session,
            queue=None,
        ) -> None:
            pass

        async def get_run(
            self,
            requested_run_id,
            *,
            user_id,
        ):
            assert requested_run_id == run_id
            assert user_id == user_id

            return run

    monkeypatch.setattr(
        "app.api.routes.runs.RunService",
        FakeRunService,
    )

    async def override_session():
        yield FakeSession()

    async def override_current_user():
        return fake_user

    app.dependency_overrides[
        get_session
    ] = override_session

    app.dependency_overrides[
        get_current_user
    ] = override_current_user

    try:
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            response = await client.get(
                f"/api/v1/runs/{run_id}",
            )

        assert response.status_code == 200

        body = response.json()

        assert body["id"] == str(run_id)
        assert body["project_id"] == str(project_id)
        assert body["status"] == "running"

        assert body["progress"] == {
            "planner": "completed",
            "researcher": "running",
            "customer": "completed",
            "competitor": "waiting",
            "tech": "waiting",
            "business": "waiting",
            "skeptic": "waiting",
            "judge": "waiting",
        }

        assert body["current_node"] is None

    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_missing_run_returns_404(
    monkeypatch,
) -> None:
    run_id = uuid.uuid4()
    user_id = uuid.uuid4()

    fake_user = SimpleNamespace(
        id=user_id,
    )

    class FakeRunService:
        def __init__(
            self,
            session,
            queue=None,
        ) -> None:
            pass

        async def get_run(
            self,
            requested_run_id,
            *,
            user_id,
        ):
            assert requested_run_id == run_id
            assert user_id == fake_user.id

            return None

    monkeypatch.setattr(
        "app.api.routes.runs.RunService",
        FakeRunService,
    )

    async def override_session():
        yield FakeSession()

    async def override_current_user():
        return fake_user

    app.dependency_overrides[
        get_session
    ] = override_session

    app.dependency_overrides[
        get_current_user
    ] = override_current_user

    try:
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            response = await client.get(
                f"/api/v1/runs/{run_id}",
            )

        assert response.status_code == 404

        body = response.json()

        assert body["error"]["code"] == (
            "RUN_NOT_FOUND"
        )

        assert body["error"]["message"] == (
            "Run not found"
        )

        assert "details" in body["error"]

    finally:
        app.dependency_overrides.clear()
