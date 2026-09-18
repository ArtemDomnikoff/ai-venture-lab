from __future__ import annotations

import pytest

from app.search.models import SearchResult
from app.search.service import SearchService


class FakeSearchProvider:
    def __init__(self, results: list[SearchResult]) -> None:
        self.results = results
        self.last_query: str | None = None
        self.last_max_results: int | None = None

    async def search(
        self,
        query: str,
        *,
        max_results: int = 5,
    ) -> list[SearchResult]:
        self.last_query = query
        self.last_max_results = max_results
        return self.results


@pytest.mark.asyncio
async def test_search_service_normalizes_results() -> None:
    provider = FakeSearchProvider(
        [
            SearchResult(
                title="  Example   title ",
                url="HTTPS://Example.COM/article/",
                snippet="  Example   snippet ",
                source="  Example source ",
                score=0.8,
            )
        ]
    )

    service = SearchService(provider)

    results = await service.search("test")

    assert len(results) == 1
    assert results[0].title == "Example title"
    assert results[0].url == "https://example.com/article"
    assert results[0].snippet == "Example snippet"
    assert results[0].source == "Example source"


@pytest.mark.asyncio
async def test_search_service_deduplicates_urls() -> None:
    provider = FakeSearchProvider(
        [
            SearchResult(
                title="First",
                url="https://example.com/article/",
                snippet="First",
                source="Example",
                score=0.6,
            ),
            SearchResult(
                title="Second",
                url="https://EXAMPLE.com/article",
                snippet="Second",
                source="Example",
                score=0.9,
            ),
        ]
    )

    service = SearchService(provider)

    results = await service.search("test")

    assert len(results) == 1
    assert results[0].title == "Second"
    assert results[0].score == 0.9


@pytest.mark.asyncio
async def test_search_service_sorts_by_score_descending() -> None:
    provider = FakeSearchProvider(
        [
            SearchResult(
                title="Low",
                url="https://example.com/low",
                snippet="Low",
                source="Example",
                score=0.2,
            ),
            SearchResult(
                title="High",
                url="https://example.com/high",
                snippet="High",
                source="Example",
                score=0.9,
            ),
            SearchResult(
                title="Medium",
                url="https://example.com/medium",
                snippet="Medium",
                source="Example",
                score=0.5,
            ),
        ]
    )

    service = SearchService(provider)

    results = await service.search("test")

    assert [result.title for result in results] == [
        "High",
        "Medium",
        "Low",
    ]


@pytest.mark.asyncio
async def test_search_service_limits_final_results() -> None:
    provider = FakeSearchProvider(
        [
            SearchResult(
                title=f"Result {index}",
                url=f"https://example.com/{index}",
                snippet=f"Result {index}",
                source="Example",
                score=float(index),
            )
            for index in range(1, 6)
        ]
    )

    service = SearchService(provider)

    results = await service.search(
        "test",
        max_results=2,
    )

    assert len(results) == 2
    assert results[0].score == 5.0
    assert results[1].score == 4.0


@pytest.mark.asyncio
async def test_search_service_passes_query_to_provider() -> None:
    provider = FakeSearchProvider([])

    service = SearchService(provider)

    await service.search(
        "startup validation market",
        max_results=3,
    )

    assert provider.last_query == "startup validation market"
    assert provider.last_max_results == 3
