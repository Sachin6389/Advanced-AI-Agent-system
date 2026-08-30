from app.agents.llm import llm
from app.tools.calculator import calculator


async def analyst_agent(
    state: dict
):

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

    response = await llm.bind_tools(
        [calculator]
    ).ainvoke(
        prompt
    )

    return {

        "analysis":
            response.content,

        "status":
            "analysis_completed"

    }