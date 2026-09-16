from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    AnalysisFailedError,
    AnalysisNotReadyError,
    ResultNotFoundError,
    RunNotFoundError,
)
from app.domain.enums import RunStatus
from app.repositories.run import RunRepository
from app.schemas.result import (
    AnalysisDecision,
    AnalysisResultResponse,
    FindingCategory,
    FindingResponse,
)


class ResultService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = RunRepository(session)

    async def get_result(
        self,
        run_id: uuid.UUID,
    ) -> AnalysisResultResponse:
        run = await self.repository.get_by_id(run_id)

        if run is None:
            raise RunNotFoundError(str(run_id))

        self._ensure_result_available(run)

        result = run.result

        if not isinstance(result, dict):
            raise ResultNotFoundError(str(run_id))

        judge = result.get("judge")

        if not isinstance(judge, dict):
            raise ResultNotFoundError(str(run_id))

        raw_score = judge.get("score")
        raw_decision = judge.get("decision")

        if not isinstance(raw_score, int):
            raise ResultNotFoundError(str(run_id))

        if not isinstance(raw_decision, str):
            raise ResultNotFoundError(str(run_id))

        try:
            decision = AnalysisDecision(raw_decision)
        except ValueError as exc:
            raise ResultNotFoundError(str(run_id)) from exc

        summary = self._build_summary(
            result=result,
            judge=judge,
        )

        return AnalysisResultResponse(
            run_id=run.id,
            score=raw_score,
            decision=decision,
            summary=summary,
            created_at=run.finished_at or run.created_at,
        )

    async def get_findings(
        self,
        run_id: uuid.UUID,
    ) -> list[FindingResponse]:
        run = await self.repository.get_by_id(run_id)

        if run is None:
            raise RunNotFoundError(str(run_id))

        self._ensure_result_available(run)

        result = run.result

        if not isinstance(result, dict):
            raise ResultNotFoundError(str(run_id))

        findings: list[FindingResponse] = []

        agent_mapping = (
            (
                "researcher",
                FindingCategory.MARKET,
                "Market research",
            ),
            (
                "customer",
                FindingCategory.CUSTOMER,
                "Customer research",
            ),
            (
                "competitor",
                FindingCategory.COMPETITION,
                "Competition research",
            ),
            (
                "tech",
                FindingCategory.TECHNOLOGY,
                "Technology research",
            ),
            (
                "business",
                FindingCategory.BUSINESS,
                "Business research",
            ),
            (
                "skeptic",
                FindingCategory.SKEPTIC,
                "Critical review",
            ),
        )

        for agent_name, category, title in agent_mapping:
            agent_result = result.get(agent_name)

            if not isinstance(agent_result, dict):
                continue

            summary = agent_result.get("summary")
            confidence = agent_result.get("confidence")

            if not isinstance(summary, str):
                continue

            if not isinstance(confidence, int):
                continue

            finding_id = uuid.uuid5(
                uuid.NAMESPACE_URL,
                f"ai-venture-lab:run:{run.id}:finding:{category.value}",
            )

            findings.append(
                FindingResponse(
                    id=finding_id,
                    category=category,
                    title=title,
                    summary=summary,
                    confidence=confidence,
                )
            )

        if not findings:
            raise ResultNotFoundError(str(run_id))

        return findings

    @staticmethod
    def _ensure_result_available(run) -> None:
        if run.status in {
            RunStatus.QUEUED,
            RunStatus.RUNNING,
        }:
            raise AnalysisNotReadyError(
                run_id=str(run.id),
                status=run.status.value,
            )

        if run.status is RunStatus.FAILED:
            raise AnalysisFailedError(
                run_id=str(run.id),
                error=run.error,
            )

        if run.status is not RunStatus.COMPLETED:
            raise ResultNotFoundError(str(run.id))

    @staticmethod
    def _build_summary(
        *,
        result: dict,
        judge: dict,
    ) -> str:
        skeptic = result.get("skeptic")

        if isinstance(skeptic, dict):
            skeptic_summary = skeptic.get("summary")

            if isinstance(skeptic_summary, str) and skeptic_summary.strip():
                return skeptic_summary

        strengths = judge.get("strengths", [])
        risks = judge.get("risks", [])

        strength_text = ", ".join(
            item
            for item in strengths
            if isinstance(item, str)
        )

        risk_text = ", ".join(
            item
            for item in risks
            if isinstance(item, str)
        )

        parts: list[str] = []

        if strength_text:
            parts.append(f"Strengths: {strength_text}")

        if risk_text:
            parts.append(f"Risks: {risk_text}")

        if parts:
            return " ".join(parts)

        return "Analysis completed."