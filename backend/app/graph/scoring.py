from __future__ import annotations

from typing import Final
from urllib.parse import urlsplit

from app.graph.schemas import AgentFinding, ScoreBreakdown
from app.graph.state import AnalysisState
from app.search.models import SearchResult

AGENT_RUBRICS: Final = {
    "researcher": {
        "demand_strength": {
            "weight": 0.25,
            "description": (
                "Strength of demonstrated demand for the problem or category."
            ),
        },
        "growth_attractiveness": {
            "weight": 0.15,
            "description": (
                "Evidence of favorable market growth or demand trends."
            ),
        },
        "market_size_evidence": {
            "weight": 0.20,
            "description": (
                "Quality and relevance of evidence for the addressable market."
            ),
        },
        "accessibility": {
            "weight": 0.15,
            "description": (
                "Realistic ability for a startup to reach and serve the market."
            ),
        },
        "market_structure": {
            "weight": 0.25,
            "description": (
                "Favorability of market structure, including fragmentation, "
                "concentration, and structural opportunity."
            ),
        },
    },
    "customer": {
        "pain_intensity": {
            "weight": 0.25,
            "description": (
                "Severity and business importance of the customer problem."
            ),
        },
        "problem_frequency": {
            "weight": 0.15,
            "description": (
                "Frequency with which target customers encounter the problem."
            ),
        },
        "willingness_to_pay": {
            "weight": 0.25,
            "description": (
                "Evidence that target customers or comparable buyers pay for "
                "solutions to the problem."
            ),
        },
        "icp_clarity": {
            "weight": 0.15,
            "description": (
                "Clarity and specificity of the ideal customer profile."
            ),
        },
        "adoption_feasibility": {
            "weight": 0.20,
            "description": (
                "Realistic ability to acquire, onboard, and convert target users."
            ),
        },
    },
    "competitor": {
        "differentiation_strength": {
            "weight": 0.25,
            "description": (
                "Strength of identifiable differentiation versus alternatives."
            ),
        },
        "competitive_gap": {
            "weight": 0.20,
            "description": (
                "Size and relevance of unmet needs left by existing alternatives."
            ),
        },
        "substitute_defensibility": {
            "weight": 0.15,
            "description": (
                "Ability to compete against indirect alternatives and substitutes."
            ),
        },
        "switching_advantage": {
            "weight": 0.15,
            "description": (
                "Potential customer advantage from switching to the proposed "
                "solution."
            ),
        },
        "defensibility": {
            "weight": 0.25,
            "description": (
                "Potential for durable protection through product, data, "
                "distribution, workflow, or other barriers."
            ),
        },
    },
    "tech": {
        "technical_feasibility": {
            "weight": 0.25,
            "description": (
                "How feasible the required technology is with known capabilities."
            ),
        },
        "implementation_manageability": {
            "weight": 0.20,
            "description": (
                "How manageable the engineering complexity is for an early-stage "
                "team."
            ),
        },
        "infrastructure_readiness": {
            "weight": 0.15,
            "description": (
                "Availability and maturity of required infrastructure and tooling."
            ),
        },
        "scalability": {
            "weight": 0.20,
            "description": (
                "Ability to scale without disproportionate technical complexity."
            ),
        },
        "time_to_mvp": {
            "weight": 0.20,
            "description": (
                "Realistic ability to reach a usable MVP in a reasonable timeframe."
            ),
        },
    },
    "business": {
        "monetization_clarity": {
            "weight": 0.20,
            "description": (
                "Clarity and plausibility of converting customer value into "
                "revenue."
            ),
        },
        "pricing_power": {
            "weight": 0.20,
            "description": (
                "Evidence that the target market can support meaningful pricing."
            ),
        },
        "unit_economics_potential": {
            "weight": 0.25,
            "description": (
                "Potential for viable unit economics based on revenue and cost "
                "drivers."
            ),
        },
        "distribution_feasibility": {
            "weight": 0.15,
            "description": (
                "Feasibility of acquiring customers through realistic channels."
            ),
        },
        "scalability": {
            "weight": 0.20,
            "description": (
                "Ability to grow without proportionally increasing cost and "
                "operational complexity."
            ),
        },
    },
}


DOMAIN_WEIGHTS: Final = {
    "researcher": 0.20,
    "customer": 0.25,
    "competitor": 0.15,
    "tech": 0.15,
    "business": 0.25,
}


SCORE_SCALE = """
Use the full 0-100 scale.

0-20: severely unfavorable, contradicted by evidence, or effectively unsupported.
21-40: weak; material problems or evidence gaps dominate.
41-60: mixed or uncertain; some support exists but important gaps remain.
61-80: favorable; meaningful supporting evidence exists.
81-100: very strong; direct, specific evidence supports a highly favorable view.

Do not default to 60-80.
A score above 80 requires strong and specific evidence.
When evidence is missing, lower the score instead of filling the gap with
plausibility.
""".strip()


CONFIDENCE_SCALE = """
Confidence is separate from the score.

0-20: almost no usable supporting evidence.
21-40: mostly indirect or incomplete evidence.
41-60: moderate evidence with material uncertainty.
61-80: good evidence supporting most of the assessment.
81-100: strong evidence from multiple relevant, preferably independent sources.
""".strip()


def scoring_instructions(
    agent_key: str,
) -> str:
    rubric = AGENT_RUBRICS.get(agent_key)

    if rubric is None:
        raise ValueError(
            f"Unknown agent rubric: {agent_key}",
        )

    dimensions = "\n".join(
        (
            f"- {dimension}: {definition['description']} "
            f"(weight {definition['weight']:.0%})"
        )
        for dimension, definition in rubric.items()
    )

    return f"""
SCORING RUBRIC

Score exactly these five dimensions:

{dimensions}

Score scale:

{SCORE_SCALE}

{CONFIDENCE_SCALE}

Rules:
- Score the opportunity in this domain, not the quality of your writing.
- Confidence is not score.
- Use the supplied web evidence as the primary basis for scoring.
- Every dimension must contain a concrete rationale.
- Every dimension should reference one or more [SOURCE n] entries when evidence
  exists.
- If a dimension cannot be supported, use an evidence_sources value of [] and
  keep the score conservative.
- Never invent a market size, price, metric, company fact, benchmark, or URL.
- The backend calculates the final domain score from these five dimensions.
""".strip()


def _domain(
    url: str,
) -> str:
    host = urlsplit(url).hostname or ""
    host = host.lower()

    return host.removeprefix(
        "www.",
    )


def _source_cap(
    source_count: int,
    domain_count: int,
) -> int:
    if source_count <= 0:
        return 40

    if source_count == 1:
        return 68

    if source_count == 2:
        return 78

    if (
        source_count >= 4
        and domain_count >= 3
    ):
        return 95

    return 86


def _evidence_support_score(
    source_count: int,
) -> int:
    if source_count <= 0:
        return 0

    if source_count == 1:
        return 40

    if source_count == 2:
        return 60

    if source_count == 3:
        return 75

    if source_count == 4:
        return 85

    return 95


def _domain_diversity_score(
    domain_count: int,
) -> int:
    if domain_count <= 0:
        return 0

    if domain_count == 1:
        return 45

    if domain_count == 2:
        return 70

    return 95


def calculate_agent_score(
    finding: AgentFinding,
    agent_key: str,
    search_results: list[SearchResult],
) -> AgentFinding:
    rubric = AGENT_RUBRICS.get(
        agent_key,
    )

    if rubric is None:
        raise ValueError(
            f"Unknown agent rubric: {agent_key}",
        )

    expected = set(rubric)
    received = [
        item.dimension
        for item in finding.dimension_scores
    ]

    if len(received) != len(
        set(received),
    ):
        raise ValueError(
            f"{agent_key} returned duplicate scoring dimensions.",
        )

    if set(received) != expected:
        missing = sorted(
            expected - set(received),
        )
        extra = sorted(
            set(received) - expected,
        )

        raise ValueError(
            f"{agent_key} returned invalid scoring dimensions. "
            f"missing={missing}, extra={extra}",
        )

    adjusted_dimensions = []

    dimension_map = {
        item.dimension: item
        for item in finding.dimension_scores
    }

    for dimension, _definition in rubric.items():
        item = dimension_map[
            dimension
        ]

        evidence_sources = sorted(
            set(
                source_index
                for source_index in item.evidence_sources
                if source_index >= 1
            )
        )

        source_count = len(
            evidence_sources,
        )

        domain_count = len(
            {
                _domain(
                    search_results[source_index - 1].url,
                )
                for source_index in evidence_sources
                if source_index
                <= len(search_results)
            }
        )

        cap = _source_cap(
            source_count=source_count,
            domain_count=domain_count,
        )

        adjusted_score = min(
            max(
                0,
                item.score,
            ),
            cap,
        )

        adjusted_item = item.model_copy(
            update={
                "score": adjusted_score,
                "evidence_sources": evidence_sources,
            }
        )

        adjusted_dimensions.append(
            adjusted_item,
        )

        dimension_map[
            dimension
        ] = adjusted_item

    weighted_score = sum(
        dimension_map[
            dimension
        ].score
        * definition["weight"]
        for dimension, definition in rubric.items()
    )

    score = max(
        0,
        min(
            100,
            int(
                round(
                    weighted_score,
                )
            ),
        ),
    )

    return finding.model_copy(
        update={
            "dimension_scores": adjusted_dimensions,
            "score": score,
        },
    )


def calculate_agent_confidence(
    finding: AgentFinding,
    search_results: list[SearchResult],
) -> AgentFinding:
    unique_evidence_urls = {
        evidence.source
        for evidence in finding.evidence
        if evidence.source.strip()
    }

    domains = {
        _domain(source)
        for source in unique_evidence_urls
    }

    relevance_by_url = {
        source.url: source.score
        for source in search_results
    }

    cited_relevance = [
        relevance_by_url[
            normalized_source
        ]
        for source in unique_evidence_urls
        for normalized_source in [source.strip()]
        if normalized_source
        in relevance_by_url
    ]

    average_relevance = (
        sum(cited_relevance)
        / len(cited_relevance)
        if cited_relevance
        else 0.0
    )

    evidence_support = _evidence_support_score(
        len(unique_evidence_urls),
    )

    domain_diversity = _domain_diversity_score(
        len(domains),
    )

    relevance_score = int(
        round(
            max(
                0,
                min(
                    100,
                    average_relevance * 100,
                ),
            )
        )
    )

    confidence = int(
        round(
            finding.confidence * 0.15
            + evidence_support * 0.45
            + domain_diversity * 0.25
            + relevance_score * 0.15
        )
    )

    confidence = max(
        5,
        min(
            95,
            confidence,
        ),
    )

    return finding.model_copy(
        update={
            "confidence": confidence,
        },
    )


def calculate_overall_score(
    state: AnalysisState,
) -> tuple[
    int,
    list[ScoreBreakdown],
    int,
]:
    breakdown: list[
        ScoreBreakdown
    ] = []

    base_score = 0.0

    for agent_key, weight in DOMAIN_WEIGHTS.items():
        finding = state[agent_key]
        score = finding.score or 0

        contribution = (
            score * weight
        )

        base_score += contribution

        breakdown.append(
            ScoreBreakdown(
                dimension=agent_key,
                score=score,
                weight=weight,
                contribution=round(
                    contribution,
                    2,
                ),
            )
        )

    skeptic = state["skeptic"]

    risk_penalty = min(
        15,
        len(skeptic.unsupported_claims)
        * 2
        + len(skeptic.contradictions)
        + len(skeptic.missing_evidence),
    )

    evidence_penalty = max(
        0,
        int(
            round(
                (
                    60
                    - skeptic.evidence_quality
                )
                * 0.05,
            )
        ),
    )

    total_penalty = min(
        30,
        risk_penalty
        + evidence_penalty,
    )

    final_score = max(
        0,
        min(
            100,
            int(
                round(
                    base_score
                    - total_penalty,
                )
            ),
        ),
    )

    return (
        final_score,
        breakdown,
        total_penalty,
    )


def decision_for_score(
    score: int,
) -> str:
    if score >= 80:
        return "strong_opportunity"

    if score >= 65:
        return "promising_but_risky"

    if score >= 50:
        return "needs_more_research"

    if score >= 35:
        return "weak_opportunity"

    return "not_recommended"


def calculate_final_confidence(
    state: AnalysisState,
) -> int:
    confidences = [
        state[key].confidence
        for key in DOMAIN_WEIGHTS
    ]

    average_agent_confidence = (
        sum(confidences)
        / len(confidences)
        if confidences
        else 0
    )

    skeptic_confidence = (
        state["skeptic"].evidence_quality
    )

    value = int(
        round(
            average_agent_confidence * 0.70
            + skeptic_confidence * 0.30
        )
    )

    return max(
        5,
        min(
            95,
            value,
        ),
    )
