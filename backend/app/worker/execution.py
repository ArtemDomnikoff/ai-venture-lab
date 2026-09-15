from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.graph.graph import build_graph
from app.observability import analysis_trace
from app.repositories.run import RunRepository


NODE_NAMES = (
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


async def run_analysis(
    session: AsyncSession,
    run_id: uuid.UUID,
    project_id: uuid.UUID,
    idea: str,
) -> dict:

    repository = RunRepository(
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
        for node in NODE_NAMES
    }

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

                    if node_name not in NODE_NAMES:
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

        except Exception as exc:
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

        output = {
            "idea": state["idea"],
            "plan": state["plan"].model_dump(),
            "researcher": state["researcher"].model_dump(),
            "customer": state["customer"].model_dump(),
            "competitor": state["competitor"].model_dump(),
            "tech": state["tech"].model_dump(),
            "business": state["business"].model_dump(),
            "skeptic": state["skeptic"].model_dump(),
            "judge": state["judge"].model_dump(),
        }

        progress = {
            node: "completed"
            for node in NODE_NAMES
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
                    "progress": progress,
                }
            )

        return output