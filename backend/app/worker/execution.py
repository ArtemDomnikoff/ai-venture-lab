from __future__ import annotations

import logging
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.graph.graph import build_graph
from app.graph.naming import generate_project_name
from app.observability import analysis_trace
from app.repositories.project import ProjectRepository
from app.repositories.run import RunRepository

logger = logging.getLogger(__name__)


GRAPH_NODE_NAMES = (
    "planner",
    "researcher",
    "customer",
    "competitor",
    "tech",
    "business",
    "skeptic",
    "judge",
)

PARALLEL_NODES = {
    "researcher",
    "customer",
    "competitor",
    "tech",
    "business",
}

NAMING_NODE = "naming"


async def run_analysis(
    session: AsyncSession,
    run_id: uuid.UUID,
    project_id: uuid.UUID,
    idea: str,
) -> dict:
    repository = RunRepository(
        session,
    )
    project_repository = ProjectRepository(
        session,
    )

    run = await repository.get_by_id(
        run_id,
    )

    if run is None:
        raise RuntimeError(
            f"Run {run_id} not found",
        )

    progress = {
        node: "waiting"
        for node in GRAPH_NODE_NAMES
    }
    progress[NAMING_NODE] = "waiting"

    await repository.update_progress(
        run,
        progress=progress,
        current_node=None,
    )

    await session.commit()

    with analysis_trace(
        run_id=str(run_id),
        project_id=str(project_id),
        idea=idea,
    ) as trace:
        graph = build_graph()

        initial_state = {
            "run_id": run_id,
            "project_id": project_id,
            "idea": idea,
        }

        progress["planner"] = "running"

        await repository.update_progress(
            run,
            progress=progress,
            current_node="planner",
        )

        await session.commit()

        state: dict = dict(
            initial_state,
        )

        try:
            async for update in graph.astream(
                initial_state,
                stream_mode="updates",
            ):
                for node_name, node_update in update.items():
                    if node_name not in GRAPH_NODE_NAMES:
                        continue

                    if isinstance(
                        node_update,
                        dict,
                    ):
                        state.update(
                            node_update,
                        )

                    progress[node_name] = "completed"

                    if node_name == "planner":
                        for parallel_node in PARALLEL_NODES:
                            progress[parallel_node] = "running"

                        current_node = None

                    elif node_name in PARALLEL_NODES:
                        all_parallel_completed = all(
                            progress[node] == "completed"
                            for node in PARALLEL_NODES
                        )

                        current_node = (
                            "skeptic"
                            if all_parallel_completed
                            else None
                        )

                        if all_parallel_completed:
                            progress["skeptic"] = "running"

                    elif node_name == "skeptic":
                        progress["judge"] = "running"
                        current_node = "judge"

                    elif node_name == "judge":
                        current_node = None

                    else:
                        current_node = node_name

                    await repository.update_progress(
                        run,
                        progress=progress,
                        current_node=current_node,
                    )

                    await session.commit()

        except Exception:
            for node_name in PARALLEL_NODES:
                if progress[node_name] == "running":
                    progress[node_name] = "failed"

            for node_name in (
                "planner",
                "skeptic",
                "judge",
            ):
                if progress[node_name] == "running":
                    progress[node_name] = "failed"

            progress[NAMING_NODE] = "waiting"

            await repository.update_progress(
                run,
                progress=progress,
                current_node=None,
            )

            await session.commit()

            if trace is not None:
                trace.update(
                    output={
                        "status": "failed",
                        "progress": progress,
                    }
                )

            raise

        #
        # Main analysis pipeline is finished here.
        #
        # judge is complete, all research is complete,
        # and only now do we run the small project-naming pipeline.
        #

        progress = {
            node: "completed"
            for node in GRAPH_NODE_NAMES
        }
        progress[NAMING_NODE] = "running"

        await repository.update_progress(
            run,
            progress=progress,
            current_node=NAMING_NODE,
        )

        await session.commit()

        generated_project_name: str | None = None
        naming_failed = False

        try:
            generated_project_name = await generate_project_name(
                idea=state["idea"],
                judge=state["judge"],
            )

            project = await project_repository.get_by_id(
                project_id,
            )

            if project is not None:
                await project_repository.update(
                    project,
                    name=generated_project_name,
                )

                await session.commit()

            progress[NAMING_NODE] = "completed"

        except Exception:
            naming_failed = True
            progress[NAMING_NODE] = "failed"

            logger.exception(
                "Project name generation failed",
                extra={
                    "event": "project.naming_failed",
                    "run_id": str(run_id),
                    "project_id": str(project_id),
                },
            )

            await session.rollback()

            #
            # The main analysis must remain successful even when the
            # optional naming step fails.
            #
            run = await repository.get_by_id(
                run_id,
            )

            if run is None:
                raise RuntimeError(
                    f"Run {run_id} disappeared during naming.",
                ) from None

        output = {
            "idea": state["idea"],
            "project_name": generated_project_name,
            "plan": state["plan"].model_dump(),
            "researcher": state["researcher"].model_dump(),
            "customer": state["customer"].model_dump(),
            "competitor": state["competitor"].model_dump(),
            "tech": state["tech"].model_dump(),
            "business": state["business"].model_dump(),
            "skeptic": state["skeptic"].model_dump(),
            "judge": state["judge"].model_dump(),
        }

        await repository.update_progress(
            run,
            progress=progress,
            current_node=None,
        )

        await session.commit()

        if trace is not None:
            trace.update(
                output={
                    "status": "completed",
                    "score": output["judge"]["score"],
                    "decision": output["judge"]["decision"],
                    "project_name": generated_project_name,
                    "naming_failed": naming_failed,
                    "progress": progress,
                }
            )

        return output
