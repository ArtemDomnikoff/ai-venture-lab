from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, patch

import pytest

from app.domain.enums import RunStatus
from app.worker.execution import run_analysis


NODE_NAMES = {
    "planner",
    "researcher",
    "customer",
    "competitor",
    "tech",
    "business",
    "skeptic",
    "judge",
}


class FakeRun:
    def __init__(
        self,
        run_id: uuid.UUID,
        project_id: uuid.UUID,
    ) -> None:
        self.id = run_id
        self.project_id = project_id
        self.status = RunStatus.RUNNING
        self.progress = {}
        self.current_node = None


class FakeRepository:
    def __init__(
        self,
        run: FakeRun,
    ) -> None:
        self.run = run
        self.update_progress_calls: list[dict] = []

    async def get_by_id(
        self,
        run_id: uuid.UUID,
    ) -> FakeRun | None:
        if run_id == self.run.id:
            return self.run

        return None

    async def update_progress(
        self,
        run: FakeRun,
        *,
        progress: dict[str, str],
        current_node: str | None = None,
    ) -> FakeRun:
        run.progress = dict(progress)
        run.current_node = current_node

        self.update_progress_calls.append(
            {
                "progress": dict(progress),
                "current_node": current_node,
            }
        )

        return run


def make_plan():
    return type(
        "Plan",
        (),
        {
            "model_dump": lambda self: {
                "market_questions": ["Market?"],
                "customer_questions": ["Customer?"],
                "competition_questions": ["Competition?"],
                "tech_questions": ["Technology?"],
                "business_questions": ["Business?"],
                "market_focus": "Market",
                "customer_focus": "Customer",
                "competition_focus": "Competition",
                "tech_focus": "Technology",
                "business_focus": "Business",
            },
            "market_questions": ["Market?"],
            "customer_questions": ["Customer?"],
            "competition_questions": ["Competition?"],
            "tech_questions": ["Technology?"],
            "business_questions": ["Business?"],
            "market_focus": "Market",
            "customer_focus": "Customer",
            "competition_focus": "Competition",
            "tech_focus": "Technology",
            "business_focus": "Business",
        },
    )()


def make_finding(name: str):
    return type(
        "Finding",
        (),
        {
            "model_dump": lambda self: {
                "summary": name,
                "claims": [f"{name} claim"],
                "evidence": [],
                "confidence": 80,
            }
        },
    )()


def make_skeptic():
    return type(
        "Skeptic",
        (),
        {
            "model_dump": lambda self: {
                "summary": "Skeptic",
                "contradictions": [],
                "unsupported_claims": [],
                "risks": ["Risk"],
                "missing_evidence": [],
                "evidence_quality": 80,
            }
        },
    )()


def make_judge():
    return type(
        "Judge",
        (),
        {
            "model_dump": lambda self: {
                "score": 80,
                "decision": "promising_but_risky",
                "strengths": ["Strength"],
                "risks": ["Risk"],
                "confidence": 80,
            }
        },
    )()


def make_updates() -> list[dict]:
    return [
        {
            "planner": {
                "plan": make_plan(),
            }
        },
        {
            "researcher": {
                "researcher": make_finding(
                    "Researcher",
                ),
            }
        },
        {
            "customer": {
                "customer": make_finding(
                    "Customer",
                ),
            }
        },
        {
            "competitor": {
                "competitor": make_finding(
                    "Competitor",
                ),
            }
        },
        {
            "tech": {
                "tech": make_finding(
                    "Tech",
                ),
            }
        },
        {
            "business": {
                "business": make_finding(
                    "Business",
                ),
            }
        },
        {
            "skeptic": {
                "skeptic": make_skeptic(),
            }
        },
        {
            "judge": {
                "judge": make_judge(),
            }
        },
    ]


class FakeAsyncStream:
    def __init__(
        self,
        updates: list[dict],
    ) -> None:
        self._updates = iter(updates)

    def __aiter__(self):
        return self

    async def __anext__(self):
        try:
            return next(self._updates)
        except StopIteration as exc:
            raise StopAsyncIteration from exc


@pytest.mark.asyncio
async def test_run_analysis_updates_progress_for_all_nodes() -> None:
    run_id = uuid.uuid4()
    project_id = uuid.uuid4()

    session = AsyncMock()

    run = FakeRun(
        run_id=run_id,
        project_id=project_id,
    )

    repository = FakeRepository(run)

    fake_graph = type(
        "FakeGraph",
        (),
        {
            "astream": lambda self, *args, **kwargs: (
                FakeAsyncStream(
                    make_updates(),
                )
            ),
        },
    )()

    with (
        patch(
            "app.worker.execution.RunRepository",
            return_value=repository,
        ),
        patch(
            "app.worker.execution.build_graph",
            return_value=fake_graph,
        ),
    ):
        result = await run_analysis(
            session=session,
            run_id=run_id,
            project_id=project_id,
            idea="AI venture evaluator",
        )

    assert result["judge"]["score"] == 80

    assert set(run.progress) == NODE_NAMES
    assert all(
        status == "completed"
        for status in run.progress.values()
    )

    assert run.current_node is None

    assert len(
        repository.update_progress_calls
    ) >= 9


@pytest.mark.asyncio
async def test_run_analysis_marks_parallel_agents_running_after_planner() -> None:
    run_id = uuid.uuid4()
    project_id = uuid.uuid4()

    session = AsyncMock()

    run = FakeRun(
        run_id=run_id,
        project_id=project_id,
    )

    repository = FakeRepository(run)

    updates = [
        {
            "planner": {
                "plan": make_plan(),
            }
        },
    ]

    fake_graph = type(
        "FakeGraph",
        (),
        {
            "astream": lambda self, *args, **kwargs: (
                FakeAsyncStream(updates)
            ),
        },
    )()

    with (
        patch(
            "app.worker.execution.RunRepository",
            return_value=repository,
        ),
        patch(
            "app.worker.execution.build_graph",
            return_value=fake_graph,
        ),
    ):
        with pytest.raises(KeyError):
            await run_analysis(
                session=session,
                run_id=run_id,
                project_id=project_id,
                idea="AI venture evaluator",
            )

    planner_progress = None

    for call in repository.update_progress_calls:
        progress = call["progress"]

        if (
            progress.get("planner") == "completed"
            and progress.get("researcher") == "running"
        ):
            planner_progress = call
            break

    assert planner_progress is not None

    progress = planner_progress["progress"]

    assert progress["customer"] == "running"
    assert progress["competitor"] == "running"
    assert progress["tech"] == "running"
    assert progress["business"] == "running"

    assert planner_progress["current_node"] is None


@pytest.mark.asyncio
async def test_run_analysis_marks_running_nodes_failed_on_error() -> None:
    run_id = uuid.uuid4()
    project_id = uuid.uuid4()

    session = AsyncMock()

    run = FakeRun(
        run_id=run_id,
        project_id=project_id,
    )

    repository = FakeRepository(run)

    class FailingGraph:
        def astream(
            self,
            *args,
            **kwargs,
        ):
            async def stream():
                yield {
                    "planner": {
                        "plan": make_plan(),
                    }
                }

                raise RuntimeError(
                    "graph failed",
                )

            return stream()

    with (
        patch(
            "app.worker.execution.RunRepository",
            return_value=repository,
        ),
        patch(
            "app.worker.execution.build_graph",
            return_value=FailingGraph(),
        ),
    ):
        with pytest.raises(
            RuntimeError,
            match="graph failed",
        ):
            await run_analysis(
                session=session,
                run_id=run_id,
                project_id=project_id,
                idea="AI venture evaluator",
            )

    assert run.progress["researcher"] == "failed"
    assert run.progress["customer"] == "failed"
    assert run.progress["competitor"] == "failed"
    assert run.progress["tech"] == "failed"
    assert run.progress["business"] == "failed"