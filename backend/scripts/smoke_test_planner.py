from __future__ import annotations

import asyncio

from app.graph.nodes.planner import planner_node
from app.graph.schemas import ResearchPlan


async def main() -> None:
    state = {
        "idea": (
            "AI assistant that analyzes startup ideas "
            "and identifies the strongest risks before founders "
            "spend money building the product."
        ),
    }

    print("Calling GPT-4o-mini...")

    result = await planner_node(state)

    plan: ResearchPlan = result["plan"]

    print("\n=== Research Plan ===")
    print(f"\nCustomer focus:\n{plan.customer_focus}")
    print(f"\nMarket focus:\n{plan.market_focus}")
    print(f"\nCompetition focus:\n{plan.competition_focus}")
    print(f"\nTech focus:\n{plan.tech_focus}")
    print(f"\nBusiness focus:\n{plan.business_focus}")

    print("\nQuestions:")
    for question in plan.questions:
        print(f"- {question}")


if __name__ == "__main__":
    asyncio.run(main())
