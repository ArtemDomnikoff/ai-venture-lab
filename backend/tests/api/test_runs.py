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
    fake_queue: FakeQueue,
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
    assert run["progress"] == {}
    assert run["current_node"] is None
    assert run["started_at"] is None
    assert run["finished_at"] is None
    assert run["error"] is None

    assert "result" not in run

    assert fake_queue.enqueued_run_ids == [
        uuid.UUID(run["id"]),
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

    data = response.json()

    assert data["error"]["code"] == "PROJECT_NOT_FOUND"
    assert data["error"]["message"] == "Project not found"
    assert data["error"]["details"]["project_id"] == str(
        project_id,
    )


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

    data = response.json()

    assert data["error"]["code"] == "RUN_NOT_FOUND"
    assert data["error"]["message"] == "Run not found"
    assert data["error"]["details"]["run_id"] == str(
        run_id,
    )


@pytest.mark.asyncio
async def test_get_project_runs(
    client: AsyncClient,
) -> None:
    project = await create_project(client)
    project_id = project["id"]

    first_response = await client.post(
        f"/api/v1/projects/{project_id}/runs",
    )

    assert first_response.status_code == 201

    first_run = first_response.json()

    # The first run is queued, so it is still active.
    # To create another run in this test, manually move it
    # to a terminal state in the database through the API-independent
    # session fixture is not available here.
    #
    # Therefore this test uses pagination against the single run.
    response = await client.get(
        f"/api/v1/projects/{project_id}/runs",
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 1
    assert data["page"] == 1
    assert data["page_size"] == 20
    assert len(data["items"]) == 1
    assert data["items"][0] == first_run


@pytest.mark.asyncio
async def test_get_project_runs_with_pagination(
    client: AsyncClient,
) -> None:
    project = await create_project(client)
    project_id = project["id"]

    first_response = await client.post(
        f"/api/v1/projects/{project_id}/runs",
    )

    assert first_response.status_code == 201

    first_run = first_response.json()

    response = await client.get(
        f"/api/v1/projects/{project_id}/runs?page=1&page_size=1",
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 1
    assert data["page"] == 1
    assert data["page_size"] == 1
    assert data["items"] == [first_run]


@pytest.mark.asyncio
async def test_get_project_runs_project_not_found(
    client: AsyncClient,
) -> None:
    project_id = uuid.uuid4()

    response = await client.get(
        f"/api/v1/projects/{project_id}/runs",
    )

    assert response.status_code == 404

    data = response.json()

    assert data["error"]["code"] == "PROJECT_NOT_FOUND"
    assert data["error"]["message"] == "Project not found"
    assert data["error"]["details"]["project_id"] == str(
        project_id,
    )


@pytest.mark.asyncio
async def test_create_multiple_runs_returns_conflict_for_active_run(
    client: AsyncClient,
) -> None:
    project = await create_project(client)
    project_id = project["id"]

    first_response = await client.post(
        f"/api/v1/projects/{project_id}/runs",
    )

    assert first_response.status_code == 201

    second_response = await client.post(
        f"/api/v1/projects/{project_id}/runs",
    )

    assert second_response.status_code == 409

    data = second_response.json()

    assert data["error"]["code"] == "RUN_ALREADY_RUNNING"
    assert data["error"]["message"] == ("Project already has an active analysis run")
    assert data["error"]["details"]["project_id"] == project_id
