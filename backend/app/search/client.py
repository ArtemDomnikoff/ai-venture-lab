from __future__ import annotations

from app.core.config import get_settings
from app.search.service import SearchService
from app.search.tavily import TavilySearchProvider


def create_search_service() -> SearchService:
    settings = get_settings()

    if not settings.tavily_api_key:
        raise RuntimeError("TAVILY_API_KEY is not configured")

    provider = TavilySearchProvider(
        api_key=settings.tavily_api_key,
    )

    return SearchService(
        provider=provider,
    )
