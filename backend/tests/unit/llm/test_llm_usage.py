from __future__ import annotations

from types import SimpleNamespace

from app.llm.usage import LLMUsage


def test_llm_usage_reads_response_usage() -> None:
    usage = SimpleNamespace(
        input_tokens=100,
        output_tokens=40,
        total_tokens=140,
        input_tokens_details=SimpleNamespace(
            cached_tokens=20,
        ),
        output_tokens_details=SimpleNamespace(
            reasoning_tokens=10,
        ),
    )

    result = LLMUsage.from_response_usage(
        usage,
    )

    assert result.input_tokens == 100
    assert result.output_tokens == 40
    assert result.total_tokens == 140
    assert result.cached_tokens == 20
    assert result.reasoning_tokens == 10


def test_llm_usage_supports_dictionary_usage() -> None:
    usage = {
        "input_tokens": 100,
        "output_tokens": 50,
        "total_tokens": 150,
        "input_tokens_details": {
            "cached_tokens": 30,
        },
        "output_tokens_details": {
            "reasoning_tokens": 5,
        },
    }

    result = LLMUsage.from_response_usage(
        usage,
    )

    assert result.input_tokens == 100
    assert result.output_tokens == 50
    assert result.total_tokens == 150
    assert result.cached_tokens == 30
    assert result.reasoning_tokens == 5


def test_llm_usage_defaults_to_zero_when_usage_is_missing() -> None:
    result = LLMUsage.from_response_usage(
        None,
    )

    assert result.input_tokens == 0
    assert result.output_tokens == 0
    assert result.total_tokens == 0
    assert result.cached_tokens == 0
    assert result.reasoning_tokens == 0


def test_llm_usage_as_dict_returns_all_metrics() -> None:
    usage = LLMUsage(
        input_tokens=100,
        output_tokens=40,
        total_tokens=140,
        cached_tokens=20,
        reasoning_tokens=10,
    )

    assert usage.as_dict() == {
        "input_tokens": 100,
        "output_tokens": 40,
        "total_tokens": 140,
        "cached_tokens": 20,
        "reasoning_tokens": 10,
    }
