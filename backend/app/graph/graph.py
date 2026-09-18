from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from app.graph.nodes.business import business_node
from app.graph.nodes.competitor import competitor_node
from app.graph.nodes.customer import customer_node
from app.graph.nodes.judge import judge_node
from app.graph.nodes.planner import planner_node
from app.graph.nodes.researcher import researcher_node
from app.graph.nodes.skeptic import skeptic_node
from app.graph.nodes.tech import tech_node
from app.graph.state import AnalysisState


def build_graph():

    graph = StateGraph(AnalysisState)

    graph.add_node(
        "planner",
        planner_node,
    )

    graph.add_node(
        "researcher",
        researcher_node,
    )

    graph.add_node(
        "customer",
        customer_node,
    )

    graph.add_node(
        "competitor",
        competitor_node,
    )

    graph.add_node(
        "tech",
        tech_node,
    )

    graph.add_node(
        "business",
        business_node,
    )

    graph.add_node(
        "skeptic",
        skeptic_node,
    )

    graph.add_node(
        "judge",
        judge_node,
    )

    #
    # START
    #

    graph.add_edge(
        START,
        "planner",
    )

    #
    # Planner fan-out
    #

    graph.add_edge(
        "planner",
        "researcher",
    )

    graph.add_edge(
        "planner",
        "customer",
    )

    graph.add_edge(
        "planner",
        "competitor",
    )

    graph.add_edge(
        "planner",
        "tech",
    )

    graph.add_edge(
        "planner",
        "business",
    )

    #
    # Fan-in barrier
    #

    graph.add_edge(
        [
            "researcher",
            "customer",
            "competitor",
            "tech",
            "business",
        ],
        "skeptic",
    )

    #
    # Final chain
    #

    graph.add_edge(
        "skeptic",
        "judge",
    )

    graph.add_edge(
        "judge",
        END,
    )

    return graph.compile()
