from __future__ import annotations

from app.graph.evidence import (
    build_search_context,
    normalize_url,
    validate_agent_evidence,
)
from app.graph.schemas import AgentFinding, Evidence
from app.search.models import SearchResult


def test_normalize_url_removes_fragment_and_trailing_slash() -> None:
    result = normalize_url("HTTPS://Example.COM/article/#section")

    assert result == "https://example.com/article"


def test_normalize_url_preserves_query_string() -> None:
    result = normalize_url("https://Example.com/search/?q=ai#section")

    assert result == "https://example.com/search?q=ai"


def test_build_search_context_contains_all_source_fields() -> None:
    results = [
        SearchResult(
            title="AI Market Report",
            url="https://example.com/report",
            snippet="The market is growing.",
            source="Example Research",
            score=0.91,
        )
    ]

    context = build_search_context(results)

    assert "[SOURCE 1]" in context
    assert "AI Market Report" in context
    assert "https://example.com/report" in context
    assert "Example Research" in context
    assert "0.910" in context
    assert "The market is growing." in context


def test_build_search_context_handles_empty_results() -> None:
    context = build_search_context([])

    assert context == "No external search results were found."


def test_validate_agent_evidence_removes_unretrieved_sources() -> None:
    search_results = [
        SearchResult(
            title="Valid source",
            url="https://example.com/valid",
            snippet="Valid evidence.",
            source="Example",
            score=0.9,
        )
    ]

    finding = AgentFinding(
        summary="Summary",
        claims=[
            "Supported claim",
            "Unsupported claim",
        ],
        evidence=[
            Evidence(
                claim="Supported claim",
                source="https://example.com/valid",
                source_type="industry_report",
                excerpt="Valid evidence.",
                confidence=90,
            ),
            Evidence(
                claim="Unsupported claim",
                source="https://not-retrieved.example/report",
                source_type="industry_report",
                excerpt="Not retrieved.",
                confidence=95,
            ),
        ],
        confidence=80,
    )

    validated = validate_agent_evidence(
        finding,
        search_results,
    )

    assert len(validated.evidence) == 1
    assert validated.evidence[0].source == "https://example.com/valid"


def test_validate_agent_evidence_accepts_normalized_url_match() -> None:
    search_results = [
        SearchResult(
            title="Valid source",
            url="https://example.com/article/",
            snippet="Valid evidence.",
            source="Example",
            score=0.9,
        )
    ]

    finding = AgentFinding(
        summary="Summary",
        claims=["Supported claim"],
        evidence=[
            Evidence(
                claim="Supported claim",
                source="HTTPS://EXAMPLE.COM/article/#section",
                source_type="web",
                excerpt="Valid evidence.",
                confidence=85,
            )
        ],
        confidence=80,
    )

    validated = validate_agent_evidence(
        finding,
        search_results,
    )

    assert len(validated.evidence) == 1


def test_validate_agent_evidence_keeps_finding_unchanged_without_evidence() -> None:
    search_results = [
        SearchResult(
            title="Source",
            url="https://example.com/source",
            snippet="Content.",
            source="Example",
            score=0.8,
        )
    ]

    finding = AgentFinding(
        summary="Summary",
        claims=["Claim"],
        evidence=[],
        confidence=60,
    )

    validated = validate_agent_evidence(
        finding,
        search_results,
    )

    assert validated.evidence == []
    assert validated.summary == finding.summary
    assert validated.claims == finding.claims
    assert validated.confidence == finding.confidence