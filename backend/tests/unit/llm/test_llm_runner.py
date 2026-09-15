from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest
from pydantic import BaseModel

from app.llm.runner import generate_structured


class OutputModel(BaseModel):
    answer: str


@pytest.mark.asyncio
async def test_generate_structured_returns_parsed_model() -> None:
    expected = OutputModel(answer="test")

    response = SimpleNamespace(
        output=[
            SimpleNamespace(
                type="message",
                content=[
                    SimpleNamespace(
                        type="output_text",
                        parsed=expected,
                    )
                ],
            )
        ]
    )

    fake_client = SimpleNamespace(
        responses=SimpleNamespace(
            parse=AsyncMock(return_value=response)
        )
    )

    fake_settings = type(
        "Settings",
        (),
        {
            "openai_model": "gpt-4o-mini",
        },
    )()

    with patch(
        "app.llm.runner.get_settings",
        return_value=fake_settings,
    ):
        result = await generate_structured(
            system_prompt="System",
            user_prompt="User",
            output_model=OutputModel,
            client=fake_client,
        )

    assert result == expected
    assert fake_client.responses.parse.await_count == 1


@pytest.mark.asyncio
async def test_generate_structured_raises_when_no_parsed_output() -> None:
    response = SimpleNamespace(
        output=[
            SimpleNamespace(
                type="message",
                content=[
                    SimpleNamespace(
                        type="output_text",
                        parsed=None,
                    )
                ],
            )
        ]
    )

    fake_client = SimpleNamespace(
        responses=SimpleNamespace(
            parse=AsyncMock(return_value=response)
        )
    )

    fake_settings = type(
        "Settings",
        (),
        {
            "openai_model": "gpt-4o-mini",
        },
    )()

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
    response = SimpleNamespace(
        output=[
            SimpleNamespace(
                type="reasoning",
                content=[],
            )
        ]
    )

    fake_client = SimpleNamespace(
        responses=SimpleNamespace(
            parse=AsyncMock(return_value=response)
        )
    )

    fake_settings = type(
        "Settings",
        (),
        {
            "openai_model": "gpt-4o-mini",
        },
    )()

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