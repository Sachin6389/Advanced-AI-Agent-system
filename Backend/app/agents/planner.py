import json

from app.agents.llm import llm
from app.schemas.plan import Plan


async def create_plan(query: str):

    prompt = f"""
You are the Planning Agent.

Break the user's complex request
into 3-6 executable steps.

Available agents:

researcher
analyst
fact_checker
reporter

Return ONLY JSON.

Format:

{{
    "steps": [
        {{
            "id": 1,
            "task": "...",
            "agent": "researcher",
            "requires_tool": true,
            "depends_on": []
        }}
    ]
}}

User request:

{query}
"""

    try:

        response = await llm.ainvoke(
            prompt
        )

        data = json.loads(
            response.content
        )

        plan = Plan.model_validate(
            data
        )

        return [
            step.model_dump()
            for step in plan.steps
        ]

    except Exception:

        return [

            {
                "id": 1,
                "task": (
                    "Research the requested topic."
                ),
                "agent": "researcher",
                "requires_tool": True,
                "depends_on": []
            },

            {
                "id": 2,
                "task": (
                    "Analyze and synthesize "
                    "the research."
                ),
                "agent": "analyst",
                "requires_tool": True,
                "depends_on": [1]
            },

            {
                "id": 3,
                "task": (
                    "Verify important claims."
                ),
                "agent": "fact_checker",
                "requires_tool": True,
                "depends_on": [2]
            },

            {
                "id": 4,
                "task": (
                    "Generate the final report."
                ),
                "agent": "reporter",
                "requires_tool": False,
                "depends_on": [3]
            }

        ]