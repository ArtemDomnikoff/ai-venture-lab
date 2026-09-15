from __future__ import annotations

from typing import TypeVar

from langfuse.openai import AsyncOpenAI
from pydantic import BaseModel

from app.core.config import get_settings
from app.llm.client import create_llm_client
from app.llm.usage import LLMUsage
from app.logging_config import get_logger


T = TypeVar(
    "T",
    bound=BaseModel,
)


logger = get_logger(__name__)


async def generate_structured(
    *,
    system_prompt: str,
    user_prompt: str,
    output_model: type[T],
    client: AsyncOpenAI | None = None,
) -> T:

    settings = get_settings()

    llm_client = (
        client
        or create_llm_client()
    )


    result, usage = await _execute_generation_with_usage(
        llm_client=llm_client,
        settings=settings,
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        output_model=output_model,
    )


    logger.info(
        "LLM generation completed",
        extra={
            "event": "llm.completed",
            "model": settings.openai_model,
            **usage.as_dict(),
        },
    )


    return result



async def _execute_generation_with_usage(
    *,
    llm_client: AsyncOpenAI,
    settings,
    system_prompt: str,
    user_prompt: str,
    output_model: type[T],
) -> tuple[T, LLMUsage]:


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


    usage = LLMUsage.from_response_usage(
        getattr(
            response,
            "usage",
            None,
        )
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


            return (
                content.parsed,
                usage,
            )


    raise RuntimeError(
        "LLM returned no message output"
    )