from __future__ import annotations

import uuid

import pytest
from httpx import AsyncClient

from tests.conftest import FakeQueue


async def create_project(client: AsyncClient) -> dict:
    response = await client.post(
        "/api/v1/projects",
        json={
            "name": "Test Project",
            "idea": "Testing startup project for Run API.",
        },
    )

    assert response.status_code == 201

    return response.json()

@pytest.mark.asyncio
async def test_create_run(
    client: AsyncClient,
    fake_queue:FakeQueue,
) -> None:
    project = await create_project(client)

    response = await client.post(
        f"/api/v1/projects/{project['id']}/runs",
    )

    assert response.status_code == 201

    run = response.json()

    assert uuid.UUID(run["id"])
    assert run["project_id"] == project["id"]
    assert run["status"] == "queued"
    assert run["started_at"] is None
    assert run["finished_at"] is None
    assert run["result"] is None
    assert run["error"] is None
    assert fake_queue.enqueued_run_ids == [
        uuid.UUID(run["id"])
    ]

@pytest.mark.asyncio
async def test_create_run_project_not_found(
    client: AsyncClient,
) -> None:
    project_id = uuid.uuid4()

    response = await client.post(
        f"/api/v1/projects/{project_id}/runs",
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Project not found",
    }

@pytest.mark.asyncio
async def test_get_run(
    client: AsyncClient,
) -> None:
    project = await create_project(client)

    create_response = await client.post(
        f"/api/v1/projects/{project['id']}/runs",
    )

    assert create_response.status_code == 201

    created_run = create_response.json()

    response = await client.get(
        f"/api/v1/runs/{created_run['id']}",
    )

    assert response.status_code == 200
    assert response.json() == created_run

@pytest.mark.asyncio
async def test_get_run_not_found(
    client: AsyncClient,
) -> None:
    run_id = uuid.uuid4()

    response = await client.get(
        f"/api/v1/runs/{run_id}",
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Run not found",
    }

@pytest.mark.asyncio
async def test_get_project_runs(
    client: AsyncClient,
) -> None:
    project = await create_project(client)
    project_id = project["id"]

    first_response = await client.post(
        f"/api/v1/projects/{project_id}/runs",
    )
    second_response = await client.post(
        f"/api/v1/projects/{project_id}/runs",
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 201

    first_run = first_response.json()
    second_run = second_response.json()

    response = await client.get(
        f"/api/v1/projects/{project_id}/runs",
    )

    assert response.status_code == 200

    runs = response.json()

    assert len(runs) == 2
    assert {run["id"] for run in runs} == {
        first_run["id"],
        second_run["id"],
    }

@pytest.mark.asyncio
async def test_get_project_runs_project_not_found(
    client: AsyncClient,
) -> None:
    project_id = uuid.uuid4()

    response = await client.get(
        f"/api/v1/projects/{project_id}/runs",
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Project not found",
    }

@pytest.mark.asyncio
async def test_create_multiple_runs(
    client: AsyncClient,
) -> None:
    project = await create_project(client)
    project_id = project["id"]

    first_response = await client.post(
        f"/api/v1/projects/{project_id}/runs",
    )
    second_response = await client.post(
        f"/api/v1/projects/{project_id}/runs",
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 201

    first_run = first_response.json()
    second_run = second_response.json()

    assert first_run["id"] != second_run["id"]
    assert first_run["project_id"] == project_id
    assert second_run["project_id"] == project_id
    assert first_run["status"] == "queued"
    assert second_run["status"] == "queued"