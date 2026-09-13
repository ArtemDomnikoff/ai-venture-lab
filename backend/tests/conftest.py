import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.db.base import Base
from app.api.deps import get_session
from app.main import app


TEST_DATABASE_URL = (
    "postgresql+asyncpg://"
    "postgres:postgres"
    "@127.0.0.1:15432/"
    "venture_lab_test"
)


@pytest_asyncio.fixture
async def engine():
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
    )

    yield engine

    await engine.dispose()


@pytest_asyncio.fixture
async def session(engine):
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with session_factory() as session:
        yield session

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client(session: AsyncSession):
    async def override_get_session():
        yield session

    app.dependency_overrides[get_session] = override_get_session

    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        yield client

    app.dependency_overrides.clear()