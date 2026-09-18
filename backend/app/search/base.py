from __future__ import annotations

from typing import Protocol

from app.search.models import SearchResult


class SearchProvider(Protocol):
    async def search(
        self,
        query: str,
        *,
        max_results: int = 5,
    ) -> list[SearchResult]: ...
