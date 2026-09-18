from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from app.search.models import SearchResult
from app.search.tavily import TavilySearchProvider


@pytest.mark.asyncio
async def test_tavily_search_provider_maps_response_to_search_results() -> None:
    response = {
        "results": [
            {
                "title": "AI Market Report",
                "url": "https://example.com/report",
                "content": "The AI market is growing.",
                "score": 0.92,
            },
            {
                "title": "AI Startup News",
                "url": "https://example.com/news",
                "content": "Startup activity increased.",
                "score": 0.81,
            },
        ]
    }

    with patch("app.search.tavily.AsyncTavilyClient") as mock_client_class:
        mock_client = mock_client_class.return_value
        mock_client.search = AsyncMock(
            return_value=response,
        )

        provider = TavilySearchProvider(
            api_key="test-key",
        )

        results = await provider.search(
            "AI startup market",
            max_results=5,
        )

    assert len(results) == 2

    assert results[0] == SearchResult(
        title="AI Market Report",
        url="https://example.com/report",
        snippet="The AI market is growing.",
        source="https://example.com/report",
        score=0.92,
    )

    assert results[1] == SearchResult(
        title="AI Startup News",
        url="https://example.com/news",
        snippet="Startup activity increased.",
        source="https://example.com/news",
        score=0.81,
    )


@pytest.mark.asyncio
async def test_tavily_search_provider_skips_invalid_results() -> None:
    response = {
        "results": [
            {
                "title": "Valid",
                "url": "https://example.com/valid",
                "content": "Valid content.",
                "score": 0.9,
            },
            {
                "title": "",
                "url": "https://example.com/no-title",
                "content": "Content.",
                "score": 0.8,
            },
            {
                "title": "No URL",
                "url": "",
                "content": "Content.",
                "score": 0.7,
            },
            {
                "title": "No content",
                "url": "https://example.com/no-content",
                "content": "",
                "score": 0.6,
            },
        ]
    }

    with patch("app.search.tavily.AsyncTavilyClient") as mock_client_class:
        mock_client = mock_client_class.return_value
        mock_client.search = AsyncMock(
            return_value=response,
        )

        provider = TavilySearchProvider(
            api_key="test-key",
        )

        results = await provider.search(
            "test",
        )

    assert len(results) == 1
    assert results[0].url == "https://example.com/valid"


@pytest.mark.asyncio
async def test_tavily_search_provider_passes_search_parameters() -> None:
    response = {
        "results": [],
    }

    with patch("app.search.tavily.AsyncTavilyClient") as mock_client_class:
        mock_client = mock_client_class.return_value
        mock_client.search = AsyncMock(
            return_value=response,
        )

        provider = TavilySearchProvider(
            api_key="test-key",
        )

        await provider.search(
            "startup competitors",
            max_results=7,
        )

    mock_client.search.assert_awaited_once_with(
        query="startup competitors",
        search_depth="advanced",
        max_results=7,
        include_answer=False,
        include_raw_content=False,
    )
