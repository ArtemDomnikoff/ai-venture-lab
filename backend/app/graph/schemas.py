from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class ResearchPlan(BaseModel):
    market_questions: list[str] = Field(
        min_length=3,
        max_length=6,
        description="Concrete questions for market research.",
    )
    market_queries: list[str] = Field(
        min_length=4,
        max_length=5,
        description="Targeted web-search queries for market research.",
    )
    customer_questions: list[str] = Field(
        min_length=3,
        max_length=6,
        description="Concrete questions for customer and ICP research.",
    )
    customer_queries: list[str] = Field(
        min_length=4,
        max_length=5,
        description="Targeted web-search queries for customer research.",
    )
    competition_questions: list[str] = Field(
        min_length=3,
        max_length=6,
        description="Concrete questions for competitor research.",
    )
    competition_queries: list[str] = Field(
        min_length=4,
        max_length=5,
        description="Targeted web-search queries for competitor research.",
    )
    tech_questions: list[str] = Field(
        min_length=3,
        max_length=6,
        description="Concrete questions for technical feasibility research.",
    )
    tech_queries: list[str] = Field(
        min_length=4,
        max_length=5,
        description="Targeted web-search queries for technical research.",
    )
    business_questions: list[str] = Field(
        min_length=3,
        max_length=6,
        description="Concrete questions for business-model research.",
    )
    business_queries: list[str] = Field(
        min_length=4,
        max_length=5,
        description="Targeted web-search queries for business research.",
    )
    customer_focus: str = Field(
        min_length=1,
        description="Main customer-research focus.",
    )
    market_focus: str = Field(
        min_length=1,
        description="Main market-research focus.",
    )
    competition_focus: str = Field(
        min_length=1,
        description="Main competition-research focus.",
    )
    tech_focus: str = Field(
        min_length=1,
        description="Main technical-research focus.",
    )
    business_focus: str = Field(
        min_length=1,
        description="Main business-research focus.",
    )


class ResearchDraft(BaseModel):
    key_findings: list[str] = Field(
        min_length=1,
        max_length=8,
        description="Important findings supported by the initial research.",
    )
    evidence_gaps: list[str] = Field(
        default_factory=list,
        max_length=8,
        description="Important unanswered questions or evidence gaps.",
    )
    follow_up_queries: list[str] = Field(
        default_factory=list,
        max_length=3,
        description="Targeted follow-up search queries to close material gaps.",
    )


class Evidence(BaseModel):
    claim: str = Field(
        min_length=1,
        description="Claim supported by this evidence.",
    )
    source: str = Field(
        min_length=1,
        description="Exact URL of a source returned by the search provider.",
    )
    source_type: str = Field(
        min_length=1,
        description=(
            "Source type such as government, research, company, news, "
            "industry_report, pricing, documentation, or community."
        ),
    )
    excerpt: str = Field(
        min_length=1,
        description="Relevant excerpt or faithful paraphrase from the source.",
    )
    confidence: int = Field(
        ge=0,
        le=100,
        description="Confidence that this source directly supports the claim.",
    )


class ScoreDimension(BaseModel):
    dimension: str = Field(
        min_length=1,
        description="Exact dimension name from the supplied scoring rubric.",
    )
    score: int = Field(
        ge=0,
        le=100,
        description="Dimension score according to the supplied rubric.",
    )
    rationale: str = Field(
        min_length=1,
        description="Concrete rationale for the score.",
    )
    evidence_sources: list[int] = Field(
        default_factory=list,
        description=(
            "1-based [SOURCE n] references that support this dimension score."
        ),
    )


class AgentFinding(BaseModel):
    summary: str = Field(
        min_length=1,
        description="Concise, evidence-grounded analysis summary.",
    )
    claims: list[str] = Field(
        min_length=3,
        max_length=12,
        description=(
            "Important claims. Prefer concrete metrics, named companies, "
            "prices, dates, percentages, or explicit evidence gaps."
        ),
    )
    evidence: list[Evidence] = Field(
        default_factory=list,
        description="Evidence supporting the claims.",
    )
    strengths: list[str] = Field(
        default_factory=list,
        max_length=8,
        description="Evidence-backed strengths in this domain.",
    )
    risks: list[str] = Field(
        default_factory=list,
        max_length=8,
        description="Important risks identified in this domain.",
    )
    opportunities: list[str] = Field(
        default_factory=list,
        max_length=8,
        description="Evidence-backed opportunities in this domain.",
    )
    dimension_scores: list[ScoreDimension] = Field(
        min_length=5,
        max_length=5,
        description="Exactly five scores required by the agent-specific rubric.",
    )
    score: int | None = Field(
        default=None,
        ge=0,
        le=100,
        description=(
            "Backend-calculated overall domain score. Do not invent this value."
        ),
    )
    confidence: int = Field(
        ge=0,
        le=100,
        description=(
            "Model-estimated confidence. The backend recalculates the final "
            "confidence from evidence support."
        ),
    )


class SkepticResult(BaseModel):
    summary: str = Field(
        min_length=1,
        description="Concise audit summary.",
    )
    contradictions: list[str] = Field(
        default_factory=list,
        description="Contradictions between research tracks.",
    )
    unsupported_claims: list[str] = Field(
        default_factory=list,
        description="Material claims that lack adequate evidence.",
    )
    risks: list[str] = Field(
        min_length=1,
        description="Important cross-domain risks.",
    )
    missing_evidence: list[str] = Field(
        default_factory=list,
        description="Important evidence gaps remaining after research.",
    )
    score_issues: list[str] = Field(
        default_factory=list,
        description="Dimensions where an agent score appears weakly supported.",
    )
    evidence_quality: int = Field(
        ge=0,
        le=100,
        description="Overall quality and coverage of the evidence base.",
    )


class ScoreBreakdown(BaseModel):
    dimension: str = Field(
        min_length=1,
    )
    score: int = Field(
        ge=0,
        le=100,
    )
    weight: float = Field(
        gt=0,
        le=1,
    )
    contribution: float = Field(
        ge=0,
    )


class JudgeNarrative(BaseModel):
    summary: str = Field(
        min_length=1,
    )
    strengths: list[str] = Field(
        min_length=1,
        max_length=8,
    )
    risks: list[str] = Field(
        min_length=1,
        max_length=8,
    )


class JudgeResult(BaseModel):
    score: int = Field(
        ge=0,
        le=100,
        description="Backend-calculated overall opportunity score.",
    )
    decision: Literal[
        "strong_opportunity",
        "promising_but_risky",
        "needs_more_research",
        "weak_opportunity",
        "not_recommended",
    ]
    summary: str = Field(
        min_length=1,
    )
    strengths: list[str] = Field(
        min_length=1,
        max_length=8,
    )
    risks: list[str] = Field(
        min_length=1,
        max_length=8,
    )
    confidence: int = Field(
        ge=0,
        le=100,
    )
    evidence_quality: int = Field(
        ge=0,
        le=100,
    )
    score_breakdown: list[ScoreBreakdown] = Field(
        min_length=5,
        max_length=5,
    )
    risk_penalty: int = Field(
        ge=0,
        le=30,
    )
