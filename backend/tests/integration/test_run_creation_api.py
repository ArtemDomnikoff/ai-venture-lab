from __future__ import annotations

import uuid
from datetime import UTC, datetime

import pytest
from httpx import ASGITransport, AsyncClient

from app.api.deps import get_queue, get_session
from app.domain.enums import RunStatus
from app.main import app


class FakeSession:
    pass


class FakeRun:
    def __init__(
        self,
        *,
        run_id: uuid.UUID,
        project_id: uuid.UUID,
    ) -> None:
        self.id = run_id
        self.project_id = project_id
        self.status = RunStatus.QUEUED
        self.progress = {
            "planner": "waiting",
            "researcher": "waiting",
            "customer": "waiting",
            "competitor": "waiting",
            "tech": "waiting",
            "business": "waiting",
            "skeptic": "waiting",
            "judge": "waiting",
        }
        self.current_node = None
        self.started_at = None
        self.finished_at = None
        self.result = None
        self.error = None
        self.created_at = datetime.now(UTC)


class FakeQueue:
    def __init__(self) -> None:
        self.enqueued_run_ids: list[uuid.UUID] = []

    async def enqueue_run(
        self,
        run_id: uuid.UUID,
    ) -> None:
        self.enqueued_run_ids.append(run_id)


@pytest.mark.asyncio
async def test_create_run_creates_queued_run_and_enqueues_it(
    monkeypatch,
) -> None:
    project_id = uuid.uuid4()
    run_id = uuid.uuid4()

    fake_session = FakeSession()
    fake_queue = FakeQueue()

    fake_run = FakeRun(
        run_id=run_id,
        project_id=project_id,
    )

    class FakeRunService:
        def __init__(
            self,
            session,
            queue=None,
        ) -> None:
            assert session is fake_session
            assert queue is fake_queue

        async def create_run(
            self,
            requested_project_id,
        ):
            assert requested_project_id == project_id

            await fake_queue.enqueue_run(
                fake_run.id,
            )

            return fake_run

    monkeypatch.setattr(
        "app.api.routes.runs.RunService",
        FakeRunService,
    )

    async def override_session():
        yield fake_session

    async def override_queue():
        return fake_queue

    app.dependency_overrides[get_session] = override_session
    app.dependency_overrides[get_queue] = override_queue

    try:
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            response = await client.post(
                f"/api/v1/projects/{project_id}/runs",
            )

        assert response.status_code == 201

        body = response.json()

        assert body["id"] == str(run_id)
        assert body["project_id"] == str(project_id)
        assert body["status"] == "queued"

        assert body["progress"] == {
            "planner": "waiting",
            "researcher": "waiting",
            "customer": "waiting",
            "competitor": "waiting",
            "tech": "waiting",
            "business": "waiting",
            "skeptic": "waiting",
            "judge": "waiting",
        }

        assert body["current_node"] is None

        assert fake_queue.enqueued_run_ids == [
            run_id,
        ]

    finally:
        app.dependency_overrides.clear()
