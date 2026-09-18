from __future__ import annotations

from pydantic import BaseModel, Field


class ResearchPlan(BaseModel):
    market_questions: list[str] = Field(
        min_length=1,
        description="Questions for market research.",
    )
    customer_questions: list[str] = Field(
        min_length=1,
        description="Questions for customer and ICP research.",
    )
    competition_questions: list[str] = Field(
        min_length=1,
        description="Questions for competitor research.",
    )
    tech_questions: list[str] = Field(
        min_length=1,
        description="Questions for technical feasibility research.",
    )
    business_questions: list[str] = Field(
        min_length=1,
        description="Questions for business model and economics research.",
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


class Evidence(BaseModel):
    claim: str = Field(
        min_length=1,
        description="Claim supported by this evidence.",
    )
    source: str = Field(
        min_length=1,
        description=("Exact URL of a source returned by the external search provider."),
    )
    source_type: str = Field(
        min_length=1,
        description=(
            "Type of source, for example company_website, news, "
            "research, government, or industry_report."
        ),
    )
    excerpt: str = Field(
        min_length=1,
        description="Relevant excerpt or paraphrase from the retrieved source.",
    )
    confidence: int = Field(
        ge=0,
        le=100,
        description="Confidence that the source supports the claim.",
    )


class AgentFinding(BaseModel):
    summary: str = Field(
        min_length=1,
        description="Concise analysis summary.",
    )
    claims: list[str] = Field(
        min_length=1,
        description="Important claims derived from the analysis.",
    )
    evidence: list[Evidence] = Field(
        default_factory=list,
        description="Evidence supporting the claims.",
    )
    confidence: int = Field(
        ge=0,
        le=100,
        description="Overall confidence in the analysis.",
    )


class SkepticResult(BaseModel):
    summary: str = Field(
        min_length=1,
        description="Concise critical review summary.",
    )
    contradictions: list[str] = Field(
        default_factory=list,
        description="Contradictions between the five agent analyses.",
    )
    unsupported_claims: list[str] = Field(
        default_factory=list,
        description="Important claims that lack adequate support.",
    )
    risks: list[str] = Field(
        min_length=1,
        description="Important risks identified during cross-review.",
    )
    missing_evidence: list[str] = Field(
        default_factory=list,
        description="Important missing evidence.",
    )
    evidence_quality: int = Field(
        ge=0,
        le=100,
        description="Overall quality of the evidence used by the five agents.",
    )


class JudgeResult(BaseModel):
    score: int = Field(
        ge=0,
        le=100,
        description="Overall startup opportunity score.",
    )
    decision: str = Field(
        min_length=1,
        description=(
            "Final decision. Recommended values are "
            "strong_opportunity, promising_but_risky, "
            "needs_more_research, weak_opportunity, or not_recommended."
        ),
    )
    strengths: list[str] = Field(
        min_length=1,
        description="Main strengths of the opportunity.",
    )
    risks: list[str] = Field(
        min_length=1,
        description="Main risks of the opportunity.",
    )
    confidence: int = Field(
        ge=0,
        le=100,
        description="Confidence in the final judgment.",
    )
