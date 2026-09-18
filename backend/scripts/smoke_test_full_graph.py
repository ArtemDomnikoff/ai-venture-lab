from app.search.models import SearchResult


class FakeSearchService:
    async def search(
        self,
        query: str,
        max_results: int = 5,
    ) -> list[SearchResult]:

        print(
            "MOCK TAVILY:",
            query,
        )

        return [
            SearchResult(
                title="Mock source",
                url="https://mock.source/test",
                snippet="Mock evidence",
                source="https://mock.source/test",
                score=1.0,
            )
        ]
