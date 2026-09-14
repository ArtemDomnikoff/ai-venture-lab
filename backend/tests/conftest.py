import os
import subprocess
import uuid
from pathlib import Path

import psycopg
import pytest
import pytest_asyncio
from app.api.deps import get_queue, get_session
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

# Test environment must be configured before importing application settings.
os.environ["APP_ENV"] = "test"
os.environ["POSTGRES_HOST"] = "127.0.0.1"
os.environ["POSTGRES_PORT"] = "15432"
os.environ["POSTGRES_DB"] = "venture_lab_test"
os.environ["POSTGRES_USER"] = "postgres"
os.environ["POSTGRES_PASSWORD"] = "postgres"

BACKEND_DIR = Path(__file__).resolve().parents[1]

TEST_SYNC_DATABASE_URL = (
    "postgresql://"
    "postgres:postgres"
    "@127.0.0.1:15432/"
    "venture_lab_test"
)

TEST_ASYNC_DATABASE_URL = (
    "postgresql+asyncpg://"
    "postgres:postgres"
    "@127.0.0.1:15432/"
    "venture_lab_test"
)


def reset_test_database() -> None:
    with psycopg.connect(TEST_SYNC_DATABASE_URL) as connection:
        connection.execute("DROP SCHEMA public CASCADE")
        connection.execute("CREATE SCHEMA public")
        connection.commit()

class FakeQueue:
    def __init__(self) -> None:
        self.enqueued_run_ids: list[uuid.UUID] = []

    async def enqueue_run(
        self,
        run_id: uuid.UUID,
    ) -> None:
        self.enqueued_run_ids.append(run_id)

@pytest.fixture
def fake_queue() -> FakeQueue:
    return FakeQueue()


@pytest.fixture(scope="session", autouse=True)
def migrated_database() -> None:
    reset_test_database()

    env = os.environ.copy()

    subprocess.run(
        ["uv", "run", "alembic", "upgrade", "head"],
        cwd=BACKEND_DIR,
        env=env,
        check=True,
    )


@pytest_asyncio.fixture
async def engine():
    engine = create_async_engine(
        TEST_ASYNC_DATABASE_URL,
        echo=False,
    )

    yield engine

    await engine.dispose()


@pytest_asyncio.fixture
async def session(engine):
    session_factory = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with session_factory() as session:
        yield session

    async with engine.begin() as connection:
        await connection.execute(
            text(
                "TRUNCATE TABLE runs, projects "
                "RESTART IDENTITY CASCADE"
            )
        )


@pytest_asyncio.fixture
async def client(
        session: AsyncSession,
        fake_queue: FakeQueue,
):
    from app.api.deps import get_session
    from app.main import app

    async def override_get_session():
        yield session

    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[get_queue] = lambda: fake_queue
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        yield client

    app.dependency_overrides.clear()

