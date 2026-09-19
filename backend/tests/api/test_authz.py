from __future__ import annotations

import uuid
from datetime import UTC, datetime

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.enums import RunStatus
from app.models.run import Run
from app.models.user import User
from tests.conftest import FakeQueue


async def create_project(
    client: AsyncClient,
) -> dict:
    response = await client.post(
        "/api/v1/projects",
        json={
            "name": "Quota Test Project",
            "idea": "A startup idea long enough for API validation.",
        },
    )

    assert response.status_code == 201

    return response.json()


async def finish_run(
    session: AsyncSession,
    run_id: str,
) -> None:
    run = await session.scalar(
        select(Run).where(
            Run.id == uuid.UUID(run_id),
        )
    )

    assert run is not None

    run.status = RunStatus.COMPLETED
    run.started_at = datetime.now(UTC)
    run.finished_at = datetime.now(UTC)

    await session.commit()


@pytest.mark.asyncio
async def test_unauthenticated_project_access_is_rejected(
    anonymous_client: AsyncClient,
) -> None:
    response = await anonymous_client.get(
        "/api/v1/projects",
    )

    assert response.status_code == 401

    data = response.json()

    assert data["error"]["code"] == "UNAUTHORIZED"


@pytest.mark.asyncio
async def test_active_run_conflict_does_not_consume_quota(
    client: AsyncClient,
    session: AsyncSession,
    test_user: User,
    fake_queue: FakeQueue,
) -> None:
    project = await create_project(client)

    first_response = await client.post(
        f"/api/v1/projects/{project['id']}/runs",
    )

    assert first_response.status_code == 201

    second_response = await client.post(
        f"/api/v1/projects/{project['id']}/runs",
    )

    assert second_response.status_code == 409

    await session.refresh(test_user)

    assert test_user.free_runs_remaining == 2
    assert len(fake_queue.enqueued_run_ids) == 1


@pytest.mark.asyncio
async def test_free_run_quota_is_exhausted_after_three_runs(
    client: AsyncClient,
    session: AsyncSession,
    test_user: User,
) -> None:
    project = await create_project(client)

    for _ in range(3):
        response = await client.post(
            f"/api/v1/projects/{project['id']}/runs",
        )

        assert response.status_code == 201

        run_id = response.json()["id"]

        await finish_run(
            session,
            run_id,
        )

    response = await client.post(
        f"/api/v1/projects/{project['id']}/runs",
    )

    assert response.status_code == 403

    data = response.json()

    assert data["error"]["code"] == "FREE_RUNS_EXHAUSTED"

    await session.refresh(test_user)

    assert test_user.free_runs_remaining == 0
