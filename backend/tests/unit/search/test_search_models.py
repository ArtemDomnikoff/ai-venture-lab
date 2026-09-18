from __future__ import annotations

from app.search.models import SearchResult


def test_search_result_accepts_valid_data() -> None:
    result = SearchResult(
        title="Example result",
        url="https://example.com/article",
        snippet="Useful information.",
        source="Example",
        score=0.85,
    )

    assert result.title == "Example result"
    assert result.url == "https://example.com/article"
    assert result.snippet == "Useful information."
    assert result.source == "Example"
    assert result.score == 0.85


def test_search_result_uses_zero_as_default_score() -> None:
    result = SearchResult(
        title="Example result",
        url="https://example.com/article",
        snippet="Useful information.",
        source="Example",
    )

    assert result.score == 0.0
