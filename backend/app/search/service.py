from __future__ import annotations

from urllib.parse import urlsplit, urlunsplit

from app.search.base import SearchProvider
from app.search.models import SearchResult


class SearchService:
    def __init__(
        self,
        provider: SearchProvider,
    ):
        self.provider = provider

    async def search(
        self,
        query: str,
        *,
        max_results: int = 5,
    ) -> list[SearchResult]:
        normalized_query = " ".join(
            query.split(),
        ).strip()

        if not normalized_query:
            return []

        results = await self.provider.search(
            normalized_query,
            max_results=max_results,
        )

        normalized = [
            self._normalize_result(
                result,
                query=normalized_query,
            )
            for result in results
        ]

        return self._rank_and_limit(
            normalized,
            max_results=max_results,
        )

    async def search_many(
        self,
        queries: list[str],
        *,
        max_results_per_query: int = 5,
        max_total_results: int = 12,
    ) -> list[SearchResult]:
        clean_queries: list[str] = []
        seen_queries: set[str] = set()

        for query in queries:
            normalized_query = " ".join(
                query.split(),
            ).strip()

            if not normalized_query:
                continue

            key = normalized_query.casefold()

            if key in seen_queries:
                continue

            seen_queries.add(key)

            clean_queries.append(
                normalized_query,
            )

        all_results: list[SearchResult] = []

        for query in clean_queries:
            try:
                results = await self.search(
                    query,
                    max_results=max_results_per_query,
                )
            except Exception:
                continue

            all_results.extend(
                results,
            )

        if not all_results:
            if clean_queries:
                raise RuntimeError(
                    "All research search queries failed or returned no results.",
                )

            return []

        return self._rank_and_limit(
            all_results,
            max_results=max_total_results,
        )

    @classmethod
    def merge_results(
        cls,
        *batches: list[SearchResult],
        max_total_results: int = 14,
    ) -> list[SearchResult]:
        flattened = [
            result
            for batch in batches
            for result in batch
        ]

        normalized = [
            cls._normalize_result(
                result,
            )
            for result in flattened
        ]

        return cls._rank_and_limit(
            normalized,
            max_results=max_total_results,
        )

    @staticmethod
    def _normalize_result(
        result: SearchResult,
        *,
        query: str | None = None,
    ) -> SearchResult:
        return result.model_copy(
            update={
                "title": " ".join(
                    result.title.split(),
                ),
                "snippet": " ".join(
                    result.snippet.split(),
                ),
                "source": " ".join(
                    result.source.split(),
                ),
                "url": SearchService._normalize_url(
                    result.url,
                ),
                "query": (
                    query
                    if query is not None
                    else result.query
                ),
            }
        )

    @staticmethod
    def _normalize_url(
        url: str,
    ) -> str:
        parsed = urlsplit(
            url.strip(),
        )

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
        unique: dict[
            str,
            SearchResult,
        ] = {}

        for result in results:
            key = result.url

            existing = unique.get(
                key,
            )

            if (
                existing is None
                or result.score > existing.score
            ):
                unique[key] = result

        return list(
            unique.values(),
        )

    @classmethod
    def _rank_and_limit(
        cls,
        results: list[SearchResult],
        *,
        max_results: int,
    ) -> list[SearchResult]:
        unique = cls._deduplicate(
            results,
        )

        ranked = sorted(
            unique,
            key=lambda result: result.score,
            reverse=True,
        )

        return ranked[
            :max_results
        ]
