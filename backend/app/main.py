from __future__ import annotations

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.api.errors import (
    app_error_handler,
    unexpected_error_handler,
    validation_error_handler,
)
from app.api.router import api_router
from app.core.config import get_settings
from app.core.exceptions import AppError
from app.db.session import AsyncSessionLocal

settings = get_settings()
app = FastAPI(
    title="AI Venture Lab API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        origin.strip()
        for origin in settings.cors_origins.split(",")
        if origin.strip()
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(
    AppError,
    app_error_handler,
)

app.add_exception_handler(
    RequestValidationError,
    validation_error_handler,
)

app.add_exception_handler(
    Exception,
    unexpected_error_handler,
)


app.include_router(
    api_router,
)


@app.get("/health")
async def health() -> dict[str, str]:
    return {
        "status": "ok",
    }


@app.get("/health/db")
async def health_db() -> dict[str, str]:
    async with AsyncSessionLocal() as session:
        await session.execute(
            text("SELECT 1"),
        )

    return {
        "database": "ok",
    }
