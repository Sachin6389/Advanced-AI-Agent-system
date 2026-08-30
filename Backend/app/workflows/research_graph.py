from langgraph.graph import (
    StateGraph,
    START,
    END
)

from app.workflows.state import (
    AgentState
)

from app.workflows.node import (
    planner_node,
    researcher_node,
    analyst_node,
    fact_checker_node,
    reporter_node,
    finish_node,
    error_node,
    document_node
)


def build_graph():

    graph = StateGraph(
        AgentState
    )

    graph.add_node(
        "planner",
        planner_node
    )
    graph.add_node(
    "document_agent",
    document_node
)

    graph.add_node(
        "researcher",
        researcher_node
    )

    graph.add_node(
        "analyst",
        analyst_node
    )

    graph.add_node(
        "fact_checker",
        fact_checker_node
    )

    graph.add_node(
        "reporter",
        reporter_node
    )

    graph.add_node(
        "finish",
        finish_node
    )

    graph.add_node(
        "error",
        error_node
    )

    graph.add_edge(
        START,
        "planner"
    )

    graph.add_edge(
        "planner",
        "researcher"
    )

    graph.add_edge(
        "researcher",
        "analyst"
    )

    graph.add_edge(
        "analyst",
        "fact_checker"
    )

    graph.add_edge(
        "fact_checker",
        "reporter"
    )

    graph.add_edge(
        "reporter",
        "finish"
    )

    graph.add_edge(
        "finish",
        END
    )

    graph.add_edge(
        "error",
        END
    )

    return graph.compile()