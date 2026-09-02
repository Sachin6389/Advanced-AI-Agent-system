from app.agents.llm import llm
from app.tools.search import web_search
import logging


async def fact_checker_agent(
    state: dict
):
    logger=logging.getLogger(__name__)
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
    logger.info("Start the fact_checker") 
    response = await llm.bind_tools(
        [web_search]
    ).ainvoke(
        prompt
    )
    logger.info("Completed the Fact-checker")

    return {

        "fact_check":
            response.content,

        "status":
            "fact_check_completed"

    }