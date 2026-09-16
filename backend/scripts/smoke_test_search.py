from __future__ import annotations

import asyncio

from app.search.client import create_search_service


async def main() -> None:
    service = create_search_service()

    query = (
        "AI startup validation software market "
        "competitors startup founders"
    )

    print(f"Searching for:\n{query}\n")

    results = await service.search(
        query,
        max_results=5,
    )

    print(f"Received {len(results)} results.\n")

    for index, result in enumerate(results, start=1):
        print(f"{index}. {result.title}")
        print(f"   URL: {result.url}")
        print(f"   Score: {result.score:.4f}")
        print(f"   Snippet: {result.snippet[:500]}")
        print()


if __name__ == "__main__":
    asyncio.run(main())