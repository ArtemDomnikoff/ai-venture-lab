from __future__ import annotations

from app.search.models import SearchResult


class MockSearchProvider:
    async def search(
        self,
        query: str,
        *,
        max_results: int = 5,
    ) -> list[SearchResult]:
        results = [
            SearchResult(
                title="Mock search result",
                url="https://example.com/mock/",
                snippet=f"Mock result for query: {query}",
                source="Mock Search",
                score=0.8,
            ),
            SearchResult(
                title="Mock search result duplicate",
                url="https://example.com/mock",
                snippet=f"Duplicate mock result for query: {query}",
                source="Mock Search",
                score=0.6,
            ),
        ]

        return results[:max_results]
