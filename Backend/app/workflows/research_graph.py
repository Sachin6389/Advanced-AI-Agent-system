
import logging

from langgraph.graph import (
    StateGraph,
    START,
    END,
)

from app.workflows.state import AgentState

from app.workflows.node import (
    planner_node,
    researcher_node,
    analyst_node,
    fact_checker_node,
    reporter_node,
    finish_node,
    error_node,
    document_node,
    email_node,
)

from app.agents.supervisor import (
    supervisor_agent,
)


logger = logging.getLogger(__name__)


# ============================================================
# SUPERVISOR NODE
# ============================================================

async def supervisor_node(
    state: AgentState,
):

    try:

        next_agent = await supervisor_agent(
            state
        )

        return {
            "next_agent": next_agent,
        }

    except Exception as exc:

        logger.exception(
            "Supervisor failed"
        )

        return {
            "next_agent": "error",
            "errors": [
                str(exc)
            ],
            "status": "failed",
        }


# ============================================================
# SUPERVISOR ROUTER
# ============================================================

def route_supervisor(
    state: AgentState,
):

    next_agent = state.get(
        "next_agent",
        "planner",
    )

    allowed = {
        "planner",
        "document",
        "send_email",
    }

    if next_agent not in allowed:

        logger.warning(
            "Invalid supervisor route: %s",
            next_agent,
        )

        return "error"

    return next_agent


# ============================================================
# BUILD GRAPH
# ============================================================

def build_graph():

    graph = StateGraph(
        AgentState
    )

    # ========================================================
    # NODES
    # ========================================================

    graph.add_node(
        "supervisor",
        supervisor_node,
    )

    graph.add_node(
        "planner",
        planner_node,
    )

    graph.add_node(
        "researcher",
        researcher_node,
    )

    graph.add_node(
        "analyst",
        analyst_node,
    )

    graph.add_node(
        "fact_checker",
        fact_checker_node,
    )

    graph.add_node(
        "reporter",
        reporter_node,
    )

    graph.add_node(
        "document",
        document_node,
    )

    graph.add_node(
        "send_email",
        email_node,
    )

    graph.add_node(
        "finish",
        finish_node,
    )

    graph.add_node(
        "error",
        error_node,
    )

    # ========================================================
    # START → SUPERVISOR
    # ========================================================

    graph.add_edge(
        START,
        "supervisor",
    )

    # ========================================================
    # SUPERVISOR ROUTING
    # ========================================================

    graph.add_conditional_edges(

        "supervisor",

        route_supervisor,

        {
            "planner": "planner",

            "document": "document",

            "send_email": "send_email",

            "error": "error",
        },
    )

    # ========================================================
    # PLANNER PIPELINE
    # ========================================================

    graph.add_edge(
        "planner",
        "researcher",
    )

    graph.add_edge(
        "researcher",
        "analyst",
    )

    graph.add_edge(
        "analyst",
        "fact_checker",
    )

    graph.add_edge(
        "fact_checker",
        "reporter",
    )

    graph.add_edge(
        "reporter",
        "finish",
    )

    # ========================================================
    # DOCUMENT
    # ========================================================

    graph.add_edge(
        "document",
        "finish",
    )

    # ========================================================
    # EMAIL
    # ========================================================

    graph.add_edge(
        "send_email",
        "finish",
    )

    # ========================================================
    # FINISH
    # ========================================================

    graph.add_edge(
        "finish",
        END,
    )

    # ========================================================
    # ERROR
    # ========================================================

    graph.add_edge(
        "error",
        END,
    )

    return graph.compile()

