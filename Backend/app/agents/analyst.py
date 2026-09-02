from app.agents.llm import llm
from app.tools.calculator import calculator
import logging


async def analyst_agent(
    state: dict
):
    logger=logging.getLogger(__name__)

    research = state.get(
        "research",
        ""
    )

    prompt = f"""
You are the Analysis Agent.

Analyze the research below.

{research}

Identify:

1. Main findings
2. Comparisons
3. Trends
4. Contradictions
5. Important numbers
6. Missing evidence

Use the calculator tool if
arithmetic is required.

Do not invent information.
"""
    logger.info("Start the Analyst")
    response = await llm.bind_tools(
        [calculator]
    ).ainvoke(
        prompt
    )
    logger.info("Completed the Analyst")

    return {

        "analysis":
            response.content,

        "status":
            "analysis_completed"

    }