from app.agents.llm import llm
from app.tools.search import web_search


async def fact_checker_agent(
    state: dict
):

    analysis = state.get(
        "analysis",
        ""
    )

    research = state.get(
        "research",
        ""
    )

    prompt = f"""
You are the Fact Checker Agent.

Verify important claims.

ANALYSIS:

{analysis}

RESEARCH:

{research}

Classify important claims as:

VERIFIED
PARTIALLY VERIFIED
UNVERIFIED
CONTRADICTED

If evidence is insufficient,
say so clearly.
"""

    response = await llm.bind_tools(
        [web_search]
    ).ainvoke(
        prompt
    )

    return {

        "fact_check":
            response.content,

        "status":
            "fact_check_completed"

    }