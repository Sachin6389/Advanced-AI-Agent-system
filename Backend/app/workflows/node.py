from app.agents.planner import (
    create_plan
)

from app.agents.researcher import (
    researcher_agent
)

from app.agents.analyst import (
    analyst_agent
)

from app.agents.fact_checker import (
    fact_checker_agent
)

from app.agents.report import (
    reporter_agent
)
from app.agents.document_agent import(document_agent)


async def planner_node(
    state
):

    plan = await create_plan(
        state["query"]
    )

    return {

        "plan": plan,

        "current_step": 0,

        "status": "planned"

    }


async def researcher_node(
    state
):

    return await researcher_agent(
        state
    )


async def analyst_node(
    state
):

    return await analyst_agent(
        state
    )

async def document_node(state):

    return await document_agent(
        state
    )

async def fact_checker_node(
    state
):

    return await fact_checker_agent(
        state
    )


async def reporter_node(
    state
):

    return await reporter_agent(
        state
    )


def finish_node(
    state
):

    return {
        "status": "completed"
    }


def error_node(
    state
):

    return {
        "status": "failed"
    }