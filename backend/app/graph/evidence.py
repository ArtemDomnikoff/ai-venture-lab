from __future__ import annotations

from urllib.parse import urlsplit, urlunsplit

from app.graph.schemas import AgentFinding
from app.search.models import SearchResult


def normalize_url(url: str) -> str:
    """
    Normalize a URL so that equivalent source URLs can be compared safely.

    Examples:
        HTTPS://Example.COM/report/
        https://example.com/report

    become:

        https://example.com/report
    """
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


def build_search_context(
    results: list[SearchResult],
) -> str:
    """
    Convert retrieved search results into a compact context for an agent.
    """
    if not results:
        return "No external search results were found."

    blocks: list[str] = []

    for index, result in enumerate(results, start=1):
        blocks.append(
            "\n".join(
                [
                    f"[SOURCE {index}]",
                    f"Title: {result.title}",
                    f"URL: {result.url}",
                    f"Source: {result.source}",
                    f"Relevance score: {result.score:.3f}",
                    f"Excerpt: {result.snippet}",
                ]
            )
        )

    return "\n\n".join(blocks)


def validate_agent_evidence(
    finding: AgentFinding,
    search_results: list[SearchResult],
) -> AgentFinding:
    """
    Keep only evidence whose source URL was actually returned
    by the search provider.

    This provides provenance validation:
    an LLM cannot introduce an arbitrary URL that was not retrieved.
    """
    allowed_urls = {
        normalize_url(result.url)
        for result in search_results
        if result.url.strip()
    }

    validated_evidence = []

    for evidence in finding.evidence:
        source = evidence.source.strip()

        if not source:
            continue

        normalized_source = normalize_url(source)

        if normalized_source not in allowed_urls:
            continue

        validated_evidence.append(
            evidence.model_copy(
                update={
                    "source": source,
                }
            )
        )

    return finding.model_copy(
        update={
            "evidence": validated_evidence,
        }
    )