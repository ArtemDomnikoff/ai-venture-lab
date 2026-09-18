from __future__ import annotations

from urllib.parse import urlsplit, urlunsplit

from app.search.base import SearchProvider
from app.search.models import SearchResult


class SearchService:
    def __init__(self, provider: SearchProvider):
        self.provider = provider

    async def search(
        self,
        query: str,
        *,
        max_results: int = 5,
    ) -> list[SearchResult]:
        results = await self.provider.search(
            query,
            max_results=max_results,
        )

        normalized = [self._normalize_result(result) for result in results]

        unique = self._deduplicate(normalized)

        ranked = sorted(
            unique,
            key=lambda result: result.score,
            reverse=True,
        )

        return ranked[:max_results]

    @staticmethod
    def _normalize_result(
        result: SearchResult,
    ) -> SearchResult:
        return result.model_copy(
            update={
                "title": " ".join(result.title.split()),
                "snippet": " ".join(result.snippet.split()),
                "source": " ".join(result.source.split()),
                "url": SearchService._normalize_url(result.url),
            }
        )

    @staticmethod
    def _normalize_url(url: str) -> str:
        parsed = urlsplit(url.strip())

        return urlunsplit(
            (
                parsed.scheme.lower(),
                parsed.netloc.lower(),
                parsed.path.rstrip("/"),
                parsed.query,
                "",
            )
        )

    @staticmethod
    def _deduplicate(
        results: list[SearchResult],
    ) -> list[SearchResult]:
        unique: dict[str, SearchResult] = {}

        for result in results:
            key = result.url

            existing = unique.get(key)

            if existing is None or result.score > existing.score:
                unique[key] = result

        return list(unique.values())
