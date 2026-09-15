from __future__ import annotations

from tavily import AsyncTavilyClient

from app.search.models import SearchResult


class TavilySearchProvider:
    def __init__(self, api_key: str) -> None:
        self.client = AsyncTavilyClient(api_key=api_key)

    async def search(
        self,
        query: str,
        *,
        max_results: int = 5,
    ) -> list[SearchResult]:
        response = await self.client.search(
            query=query,
            search_depth="advanced",
            max_results=max_results,
            include_answer=False,
            include_raw_content=False,
        )

        results: list[SearchResult] = []

        for item in response.get("results", []):
            title = item.get("title", "")
            url = item.get("url", "")
            content = item.get("content", "")
            score = item.get("score", 0.0)

            if not title or not url or not content:
                continue

            results.append(
                SearchResult(
                    title=title,
                    url=url,
                    snippet=content,
                    source=url,
                    score=float(score),
                )
            )

        return results