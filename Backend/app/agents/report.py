from app.agents.llm import llm
import logging


async def reporter_agent(
    state: dict
):
    logger=logging.getLogger(__name__)

    prompt = f"""
You are the Report Agent.

Create a professional research report.

RESEARCH:

{state.get("research", "")}

ANALYSIS:

{state.get("analysis", "")}

FACT CHECK:

{state.get("fact_check", "")}

SOURCES:

{state.get("sources", [])}

Use this structure:

# Executive Summary

# Research Findings

# Analysis

# Fact Check

# Risks and Limitations

# Conclusion

# Sources

Do not fabricate facts
or citations.
"""
    logger.info("Start the Report Gen.")

    response = await llm.ainvoke(
        prompt
    )
    logger.info("Complete the report")

    return {

        "report":
            response.content,

        "status":
            "report_completed"

    }