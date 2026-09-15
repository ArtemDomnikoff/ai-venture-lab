from __future__ import annotations

from typing import TypeVar

from openai import AsyncOpenAI
from pydantic import BaseModel

from app.core.config import get_settings
from app.llm.client import create_llm_client


T = TypeVar("T", bound=BaseModel)


async def generate_structured(
    *,
    system_prompt: str,
    user_prompt: str,
    output_model: type[T],
    client: AsyncOpenAI | None = None,
) -> T:
    settings = get_settings()

    llm_client = client or create_llm_client()

    response = await llm_client.responses.parse(
        model=settings.openai_model,
        input=[
            {
                "role": "developer",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
        text_format=output_model,
    )

    for output in response.output:
        if output.type != "message":
            continue

        for content in output.content:
            if content.type != "output_text":
                continue

            if content.parsed is None:
                raise RuntimeError(
                    "LLM returned no structured output"
                )

            return content.parsed

    raise RuntimeError("LLM returned no message output")