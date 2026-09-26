from __future__ import annotations

from pydantic import BaseModel, Field

from app.graph.schemas import JudgeResult
from app.llm.runner import generate_structured
from app.observability import agent_trace


class ProjectNameResult(BaseModel):
    name: str = Field(
        min_length=3,
        max_length=80,
        description="Concise project title.",
    )


SYSTEM_PROMPT = """
You generate the final project title for a startup idea.

The title is a PROJECT TITLE, not a company brand name.

Rules:
- return exactly one title;
- use the same language as the startup idea;
- keep it concise: ideally 2-6 words;
- describe the product or the core idea clearly;
- make it specific enough to understand what the project is about;
- avoid generic titles like "AI Startup", "New Project", or "Startup Idea";
- avoid marketing slogans;
- avoid words like "NextGen", "Revolutionary", "Ultimate", or "Smart"
  unless they are genuinely part of the idea;
- do not mention the evaluation result, score, risks, or decision;
- do not use quotation marks;
- do not add a subtitle;
- do not add an explanation.

Return only the structured project title.
""".strip()


def _normalize_name(value: str) -> str:
    name = " ".join(
        value.split(),
    ).strip(
        " \t\n\r\"'`",
    )

    if not name:
        raise RuntimeError(
            "Project name generation returned an empty name.",
        )

    if len(name) > 80:
        name = name[:80].rsplit(
            " ",
            1,
        )[0].strip()

    if len(name) < 3:
        raise RuntimeError(
            "Project name generation returned an invalid name.",
        )

    return name


async def generate_project_name(
    *,
    idea: str,
    judge: JudgeResult,
) -> str:
    with agent_trace(
        agent_name="naming",
        run_id="",
        project_id="",
        idea=idea,
        input_data={
            "source": "idea_and_judge_summary",
        },
    ) as observation:
        user_prompt = f"""
Startup idea:

{idea}

Final analysis summary:

{judge.summary}

Generate the final project title.

The title must represent the startup idea itself, not its evaluation.
""".strip()

        result = await generate_structured(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            output_model=ProjectNameResult,
        )

        name = _normalize_name(
            result.name,
        )

        if observation is not None:
            observation.update(
                output={
                    "name": name,
                },
            )

        return name
