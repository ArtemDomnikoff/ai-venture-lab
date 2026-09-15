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
            "idea": (
                "AI assistant for reducing "
                "unnecessary AWS infrastructure costs."
            ),
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert uuid.UUID(data["id"])
    assert data["name"] == "AWS Cost AI"
    assert data["status"] == "draft"
    assert "created_at" in data
    assert "updated_at" in data

@pytest.mark.asyncio
async def test_get_projects(
    client: AsyncClient,
) -> None:
    await client.post(
        "/api/v1/projects",
        json={
            "name": "Project One",
            "idea": "This is the first project idea.",
        },
    )

    await client.post(
        "/api/v1/projects",
        json={
            "name": "Project Two",
            "idea": "This is the second project idea.",
        },
    )

    response = await client.get(
        "/api/v1/projects",
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2
    assert data[0]["name"] == "Project Two"
    assert data[1]["name"] == "Project One"

@pytest.mark.asyncio
async def test_get_project(
    client: AsyncClient,
) -> None:
    create_response = await client.post(
        "/api/v1/projects",
        json={
            "name": "AWS Cost AI",
            "idea": "AI tool for optimizing cloud infrastructure costs.",
        },
    )

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
    project_id = "00000000-0000-0000-0000-000000000000"

    response = await client.get(
        f"/api/v1/projects/{project_id}",
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Project not found",
    }

@pytest.mark.asyncio
async def test_delete_project(
    client: AsyncClient,
) -> None:
    create_response = await client.post(
        "/api/v1/projects",
        json={
            "name": "Temporary Project",
            "idea": "This project will be deleted in the test.",
        },
    )

    project_id = create_response.json()["id"]

    delete_response = await client.delete(
        f"/api/v1/projects/{project_id}",
    )

    assert delete_response.status_code == 204

    get_response = await client.get(
        f"/api/v1/projects/{project_id}",
    )

    assert get_response.status_code == 404

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