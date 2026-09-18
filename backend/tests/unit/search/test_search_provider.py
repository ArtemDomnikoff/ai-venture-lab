from __future__ import annotations

import pytest

from app.search.mock import MockSearchProvider


@pytest.mark.asyncio
async def test_mock_search_provider_returns_results() -> None:
    provider = MockSearchProvider()

    results = await provider.search(
        "AI startup validation",
        max_results=5,
    )

    assert len(results) == 2

    assert results[0].title == "Mock search result"
    assert results[0].url == "https://example.com/mock/"
    assert results[0].score == 0.8

    assert results[1].title == "Mock search result duplicate"
    assert results[1].url == "https://example.com/mock"
    assert results[1].score == 0.6


@pytest.mark.asyncio
async def test_mock_search_provider_respects_max_results() -> None:
    provider = MockSearchProvider()

    results = await provider.search(
        "AI startup validation",
        max_results=1,
    )

    assert len(results) == 1
