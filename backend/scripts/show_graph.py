from __future__ import annotations

from app.graph.graph import build_graph


def main() -> None:
    graph = build_graph()

    print("=" * 80)
    print("LANGGRAPH MERMAID")
    print("=" * 80)

    mermaid = graph.get_graph().draw_mermaid()

    print(mermaid)

    print("=" * 80)
    print("END")
    print("=" * 80)


if __name__ == "__main__":
    main()
