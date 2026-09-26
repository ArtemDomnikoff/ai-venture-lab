from __future__ import annotations

from pydantic import BaseModel, Field


class SearchResult(BaseModel):
    title: str = Field(
        min_length=1,
    )
    url: str = Field(
        min_length=1,
    )
    snippet: str = Field(
        min_length=1,
    )
    source: str = Field(
        min_length=1,
    )
    score: float = Field(
        default=0.0,
        ge=0.0,
    )
    query: str = Field(
        default="",
    )
    raw_content: str | None = None
    published_date: str | None = None
