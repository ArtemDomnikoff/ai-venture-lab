from __future__ import annotations

from langfuse.openai import AsyncOpenAI

from app.core.config import get_settings


def create_llm_client() -> AsyncOpenAI:
    settings = get_settings()

    if not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY is not configured")

    return AsyncOpenAI(
        api_key=settings.openai_api_key,
    )
