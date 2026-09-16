from __future__ import annotations

import time

from app.observability import tool_trace
from app.search.models import SearchResult
from tavily import AsyncTavilyClient


class TavilySearchProvider:
    def __init__(
        self,
        api_key: str,
    ) -> None:
        self.client = AsyncTavilyClient(
            api_key=api_key,
        )

    async def search(
        self,
        query: str,
        *,
        max_results: int = 5,
    ) -> list[SearchResult]:
        started_at = time.perf_counter()

        with tool_trace(
            tool_name="tavily.search",
            input_data={
                "query": query,
                "max_results": max_results,
                "search_depth": "advanced",
            },
        ) as observation:

            response = await self.client.search(
                query=query,
                search_depth="advanced",
                max_results=max_results,
                include_answer=False,
                include_raw_content=False,
            )

            results: list[SearchResult] = []

            for item in response.get(
                "results",
                [],
            ):
                title = item.get(
                    "title",
                    "",
                )

                url = item.get(
                    "url",
                    "",
                )

                content = item.get(
                    "content",
                    "",
                )

                score = item.get(
                    "score",
                    0.0,
                )

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

            if observation is not None:
                observation.update(
                    output={
                        "result_count": len(results),
                        "urls": [
                            result.url
                            for result in results
                        ],
                        "duration_ms": round(
                            (
                                time.perf_counter()
                                - started_at
                            )
                            * 1000,
                            2,
                        ),
                    }
                )

            return results