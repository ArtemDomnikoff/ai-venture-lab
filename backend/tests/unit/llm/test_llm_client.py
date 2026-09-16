from __future__ import annotations

from unittest.mock import patch

import pytest

from app.llm.client import create_llm_client


def test_create_llm_client_requires_api_key() -> None:
    with patch(
        "app.llm.client.get_settings",
        return_value=type(
            "Settings",
            (),
            {
                "openai_api_key": None,
            },
        )(),
    ):
        with pytest.raises(
            RuntimeError,
            match="OPENAI_API_KEY is not configured",
        ):
            create_llm_client()


def test_create_llm_client_uses_configured_key() -> None:
    fake_settings = type(
        "Settings",
        (),
        {
            "openai_api_key": "test-key",
        },
    )()

    with (
        patch(
            "app.llm.client.get_settings",
            return_value=fake_settings,
        ),
        patch("app.llm.client.AsyncOpenAI") as mock_client,
    ):
        client = create_llm_client()

    mock_client.assert_called_once_with(api_key="test-key")
    assert client == mock_client.return_value