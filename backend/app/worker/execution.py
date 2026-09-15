from __future__ import annotations

import uuid

from app.graph.graph import build_graph


async def run_analysis(
    run_id: uuid.UUID,
    project_id: uuid.UUID,
    idea: str,
) -> dict:
    graph = build_graph()

    result = await graph.ainvoke(
        {
            "run_id": run_id,
            "project_id": project_id,
            "idea": idea,
        }
    )

    return {
        "idea": result["idea"],
        "plan": result["plan"].model_dump(),
        "researcher": result["researcher"].model_dump(),
        "customer": result["customer"].model_dump(),
        "competitor": result["competitor"].model_dump(),
        "tech": result["tech"].model_dump(),
        "business": result["business"].model_dump(),
        "skeptic": result["skeptic"].model_dump(),
        "judge": result["judge"].model_dump(),
    }