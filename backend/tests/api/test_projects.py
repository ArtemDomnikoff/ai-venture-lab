from __future__ import annotations

import uuid

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_project(
    client: AsyncClient,
) -> None:
    response = await client.post(
        "/api/v1/projects",
        json={
            "name": "AWS Cost AI",
            "idea": ("AI assistant for reducing unnecessary AWS infrastructure costs."),
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert uuid.UUID(data["id"])
    assert data["name"] == "AWS Cost AI"
    assert data["idea"] == (
        "AI assistant for reducing unnecessary AWS infrastructure costs."
    )
    assert data["status"] == "draft"
    assert "created_at" in data
    assert "updated_at" in data


@pytest.mark.asyncio
async def test_get_projects(
    client: AsyncClient,
) -> None:
    first_response = await client.post(
        "/api/v1/projects",
        json={
            "name": "Project One",
            "idea": "This is the first project idea.",
        },
    )

    second_response = await client.post(
        "/api/v1/projects",
        json={
            "name": "Project Two",
            "idea": "This is the second project idea.",
        },
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 201

    response = await client.get(
        "/api/v1/projects",
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 2
    assert data["page"] == 1
    assert data["page_size"] == 20
    assert len(data["items"]) == 2

    assert data["items"][0]["name"] == "Project Two"
    assert data["items"][1]["name"] == "Project One"


@pytest.mark.asyncio
async def test_get_projects_with_pagination(
    client: AsyncClient,
) -> None:
    for index in range(3):
        response = await client.post(
            "/api/v1/projects",
            json={
                "name": f"Project {index}",
                "idea": (f"This is test project idea number {index}."),
            },
        )

        assert response.status_code == 201

    response = await client.get(
        "/api/v1/projects?page=2&page_size=2",
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 3
    assert data["page"] == 2
    assert data["page_size"] == 2
    assert len(data["items"]) == 1
    assert data["items"][0]["name"] == "Project 0"


@pytest.mark.asyncio
async def test_get_projects_invalid_pagination(
    client: AsyncClient,
) -> None:
    response = await client.get(
        "/api/v1/projects?page=0&page_size=101",
    )

    assert response.status_code == 422

    data = response.json()

    assert data["error"]["code"] == "VALIDATION_ERROR"
    assert data["error"]["message"] == ("Request validation failed")


@pytest.mark.asyncio
async def test_get_project(
    client: AsyncClient,
) -> None:
    create_response = await client.post(
        "/api/v1/projects",
        json={
            "name": "AWS Cost AI",
            "idea": ("AI tool for optimizing cloud infrastructure costs."),
        },
    )

    assert create_response.status_code == 201

    project_id = create_response.json()["id"]

    response = await client.get(
        f"/api/v1/projects/{project_id}",
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == project_id
    assert data["name"] == "AWS Cost AI"


@pytest.mark.asyncio
async def test_get_project_not_found(
    client: AsyncClient,
) -> None:
    project_id = uuid.uuid4()

    response = await client.get(
        f"/api/v1/projects/{project_id}",
    )

    assert response.status_code == 404

    data = response.json()

    assert data["error"]["code"] == "PROJECT_NOT_FOUND"
    assert data["error"]["message"] == "Project not found"
    assert data["error"]["details"]["project_id"] == str(
        project_id,
    )


@pytest.mark.asyncio
async def test_delete_project(
    client: AsyncClient,
) -> None:
    create_response = await client.post(
        "/api/v1/projects",
        json={
            "name": "Temporary Project",
            "idea": ("This project will be deleted in the test."),
        },
    )

    assert create_response.status_code == 201

    project_id = create_response.json()["id"]

    delete_response = await client.delete(
        f"/api/v1/projects/{project_id}",
    )

    assert delete_response.status_code == 204

    get_response = await client.get(
        f"/api/v1/projects/{project_id}",
    )

    assert get_response.status_code == 404

    data = get_response.json()

    assert data["error"]["code"] == "PROJECT_NOT_FOUND"


@pytest.mark.asyncio
async def test_create_project_validation(
    client: AsyncClient,
) -> None:
    response = await client.post(
        "/api/v1/projects",
        json={
            "name": "",
            "idea": "short",
        },
    )

    assert response.status_code == 422

    data = response.json()

    assert data["error"]["code"] == "VALIDATION_ERROR"
    assert data["error"]["message"] == ("Request validation failed")


@pytest.mark.asyncio
async def test_update_project(
    client: AsyncClient,
) -> None:
    create_response = await client.post(
        "/api/v1/projects",
        json={
            "name": "Original Name",
            "idea": "Original startup idea for testing.",
        },
    )

    assert create_response.status_code == 201

    project_id = create_response.json()["id"]

    response = await client.patch(
        f"/api/v1/projects/{project_id}",
        json={
            "name": "Updated Name",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == project_id
    assert data["name"] == "Updated Name"
    assert data["idea"] == "Original startup idea for testing."


@pytest.mark.asyncio
async def test_update_project_not_found(
    client: AsyncClient,
) -> None:
    project_id = uuid.uuid4()

    response = await client.patch(
        f"/api/v1/projects/{project_id}",
        json={
            "name": "Updated Name",
        },
    )

    assert response.status_code == 404

    data = response.json()

    assert data["error"]["code"] == "PROJECT_NOT_FOUND"
    assert data["error"]["message"] == "Project not found"


@pytest.mark.asyncio
async def test_update_project_requires_at_least_one_field(
    client: AsyncClient,
) -> None:
    project_id = uuid.uuid4()

    response = await client.patch(
        f"/api/v1/projects/{project_id}",
        json={},
    )

    assert response.status_code == 422

    data = response.json()

    assert data["error"]["code"] == "VALIDATION_ERROR"
