from __future__ import annotations

from urllib.parse import urlsplit, urlunsplit

from app.graph.schemas import AgentFinding
from app.search.models import SearchResult


def normalize_url(
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


def build_search_context(
    results: list[SearchResult],
) -> str:
    if not results:
        return "No external search results were found."

    blocks: list[str] = []

    for index, result in enumerate(
        results,
        start=1,
    ):
        block = [
            f"[SOURCE {index}]",
            f"Query: {result.query or 'unknown'}",
            f"Title: {result.title}",
            f"URL: {result.url}",
            f"Relevance score: {result.score:.3f}",
        ]

        if result.published_date:
            block.append(
                f"Published: {result.published_date}",
            )

        block.append(
            f"Search excerpt: {result.snippet[:1800]}",
        )

        if result.raw_content:
            block.append(
                "Page content excerpt:",
            )
            block.append(
                result.raw_content[:2200],
            )

        blocks.append(
            "\n".join(block),
        )

    return "\n\n".join(
        blocks,
    )


def validate_agent_evidence(
    finding: AgentFinding,
    search_results: list[SearchResult],
) -> AgentFinding:
    canonical_urls = {
        normalize_url(result.url): result.url
        for result in search_results
        if result.url.strip()
    }

    validated_evidence = []

    for evidence in finding.evidence:
        source = evidence.source.strip()

        if not source:
            continue

        normalized_source = normalize_url(
            source,
        )

        canonical_source = canonical_urls.get(
            normalized_source,
        )

        if canonical_source is None:
            continue

        validated_evidence.append(
            evidence.model_copy(
                update={
                    "source": canonical_source,
                }
            )
        )

    validated_evidence_urls = {
        normalize_url(
            evidence.source,
        )
        for evidence in validated_evidence
    }

    validated_dimensions = []

    for dimension in finding.dimension_scores:
        source_indexes = sorted(
            set(
                index
                for index in dimension.evidence_sources
                if (
                    1 <= index <= len(search_results)
                    and normalize_url(
                        search_results[index - 1].url,
                    )
                    in validated_evidence_urls
                )
            )
        )

        validated_dimensions.append(
            dimension.model_copy(
                update={
                    "evidence_sources": source_indexes,
                }
            )
        )

    return finding.model_copy(
        update={
            "evidence": validated_evidence,
            "dimension_scores": validated_dimensions,
        }
    )


def merge_search_results(
    *batches: list[SearchResult],
    max_total_results: int = 14,
) -> list[SearchResult]:
    unique: dict[
        str,
        SearchResult,
    ] = {}

    for batch in batches:
        for result in batch:
            normalized = normalize_url(
                result.url,
            )

            existing = unique.get(
                normalized,
            )

            if (
                existing is None
                or result.score > existing.score
            ):
                unique[
                    normalized
                ] = result

    return sorted(
        unique.values(),
        key=lambda result: result.score,
        reverse=True,
    )[
        :max_total_results
    ]
