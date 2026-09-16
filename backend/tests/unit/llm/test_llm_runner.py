from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest
from pydantic import BaseModel

from app.llm.runner import generate_structured


class OutputModel(BaseModel):
    answer: str


def make_response(
    *,
    parsed,
    usage=None,
    output_type: str = "message",
):
    return SimpleNamespace(
        usage=usage,
        output=[
            SimpleNamespace(
                type=output_type,
                content=[
                    SimpleNamespace(
                        type="output_text",
                        parsed=parsed,
                    )
                ],
            )
        ],
    )


def make_client(response):
    return SimpleNamespace(
        responses=SimpleNamespace(
            parse=AsyncMock(
                return_value=response,
            )
        )
    )


def make_settings():
    return type(
        "Settings",
        (),
        {
            "openai_model": "gpt-4o-mini",
        },
    )()


@pytest.mark.asyncio
async def test_generate_structured_returns_parsed_model() -> None:
    expected = OutputModel(
        answer="test",
    )

    usage = SimpleNamespace(
        input_tokens=10,
        output_tokens=5,
        total_tokens=15,
        input_tokens_details=SimpleNamespace(
            cached_tokens=2,
        ),
        output_tokens_details=SimpleNamespace(
            reasoning_tokens=1,
        ),
    )

    response = make_response(
        parsed=expected,
        usage=usage,
    )

    fake_client = make_client(response)
    fake_settings = make_settings()

    with (
        patch(
            "app.llm.runner.get_settings",
            return_value=fake_settings,
        ),
        patch(
            "app.llm.runner.logger",
        ) as mock_logger,
    ):
        result = await generate_structured(
            system_prompt="System",
            user_prompt="User",
            output_model=OutputModel,
            client=fake_client,
        )

    assert result == expected

    mock_logger.info.assert_called_once_with(
        "LLM generation completed",
        extra={
            "event": "llm.completed",
            "model": "gpt-4o-mini",
            "input_tokens": 10,
            "output_tokens": 5,
            "total_tokens": 15,
            "cached_tokens": 2,
            "reasoning_tokens": 1,
        },
    )

    fake_client.responses.parse.assert_awaited_once_with(
        model="gpt-4o-mini",
        input=[
            {
                "role": "developer",
                "content": "System",
            },
            {
                "role": "user",
                "content": "User",
            },
        ],
        text_format=OutputModel,
    )


@pytest.mark.asyncio
async def test_generate_structured_handles_missing_usage() -> None:
    expected = OutputModel(
        answer="test",
    )

    response = make_response(
        parsed=expected,
        usage=None,
    )

    fake_client = make_client(response)
    fake_settings = make_settings()

    with (
        patch(
            "app.llm.runner.get_settings",
            return_value=fake_settings,
        ),
        patch(
            "app.llm.runner.logger",
        ) as mock_logger,
    ):
        result = await generate_structured(
            system_prompt="System",
            user_prompt="User",
            output_model=OutputModel,
            client=fake_client,
        )

    assert result == expected

    mock_logger.info.assert_called_once_with(
        "LLM generation completed",
        extra={
            "event": "llm.completed",
            "model": "gpt-4o-mini",
            "input_tokens": 0,
            "output_tokens": 0,
            "total_tokens": 0,
            "cached_tokens": 0,
            "reasoning_tokens": 0,
        },
    )


@pytest.mark.asyncio
async def test_generate_structured_raises_when_no_parsed_output() -> None:
    response = make_response(
        parsed=None,
        usage=None,
    )

    fake_client = make_client(response)
    fake_settings = make_settings()

    with (
        patch(
            "app.llm.runner.get_settings",
            return_value=fake_settings,
        ),
        pytest.raises(
            RuntimeError,
            match="LLM returned no structured output",
        ),
    ):
        await generate_structured(
            system_prompt="System",
            user_prompt="User",
            output_model=OutputModel,
            client=fake_client,
        )


@pytest.mark.asyncio
async def test_generate_structured_raises_when_no_message_output() -> None:
    response = make_response(
        parsed=None,
        usage=None,
        output_type="reasoning",
    )

    fake_client = make_client(response)
    fake_settings = make_settings()

    with (
        patch(
            "app.llm.runner.get_settings",
            return_value=fake_settings,
        ),
        pytest.raises(
            RuntimeError,
            match="LLM returned no message output",
        ),
    ):
        await generate_structured(
            system_prompt="System",
            user_prompt="User",
            output_model=OutputModel,
            client=fake_client,
        )