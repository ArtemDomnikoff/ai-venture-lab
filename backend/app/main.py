from fastapi import FastAPI
from sqlalchemy import text
from app.redis import redis_client
from app.api.router import api_router

from app.db.session import AsyncSessionLocal

app = FastAPI(
    title="AI Venture Lab API",
    version="0.1.0",
)

app.include_router(api_router)

@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/health/db")
async def health_db() -> dict[str, str]:
    async with AsyncSessionLocal() as session:
        await session.execute(text("SELECT 1"))

    return {"database": "ok"}

@app.get("/health/redis")
async def health_redis() -> dict[str, str]:
    result = await redis_client.ping()

    if not result:
        return {"redis": "error"}

    return {"redis": "ok"}