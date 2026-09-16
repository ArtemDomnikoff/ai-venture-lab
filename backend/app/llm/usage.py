from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class LLMUsage:
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    cached_tokens: int = 0
    reasoning_tokens: int = 0

    @classmethod
    def from_response_usage(
        cls,
        usage: Any,
    ) -> "LLMUsage":
        if usage is None:
            return cls()

        input_tokens = _get_int(
            usage,
            "input_tokens",
        )

        output_tokens = _get_int(
            usage,
            "output_tokens",
        )

        total_tokens = _get_int(
            usage,
            "total_tokens",
        )

        input_details = _get_value(
            usage,
            "input_tokens_details",
        )

        output_details = _get_value(
            usage,
            "output_tokens_details",
        )

        cached_tokens = _get_int(
            input_details,
            "cached_tokens",
        )

        reasoning_tokens = _get_int(
            output_details,
            "reasoning_tokens",
        )

        return cls(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            cached_tokens=cached_tokens,
            reasoning_tokens=reasoning_tokens,
        )

    def as_dict(self) -> dict[str, int]:
        return {
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "total_tokens": self.total_tokens,
            "cached_tokens": self.cached_tokens,
            "reasoning_tokens": self.reasoning_tokens,
        }


def _get_value(
    obj: Any,
    field: str,
) -> Any:
    if obj is None:
        return None

    if isinstance(obj, dict):
        return obj.get(field)

    return getattr(
        obj,
        field,
        None,
    )


def _get_int(
    obj: Any,
    field: str,
) -> int:
    value = _get_value(
        obj,
        field,
    )

    if value is None:
        return 0

    try:
        return int(value)
    except (TypeError, ValueError):
        return 0