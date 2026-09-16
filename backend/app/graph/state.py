from __future__ import annotations

import uuid
from typing import TypedDict

from app.graph.schemas import (
    AgentFinding,
    JudgeResult,
    ResearchPlan,
    SkepticResult,
)


class AnalysisState(TypedDict, total=False):
    run_id: uuid.UUID
    project_id: uuid.UUID
    idea: str

    plan: ResearchPlan

    researcher: AgentFinding
    customer: AgentFinding
    competitor: AgentFinding
    tech: AgentFinding
    business: AgentFinding

    skeptic: SkepticResult
    judge: JudgeResult

    progress: dict[str, str]
    current_node: str | None
    errors: dict[str, str]