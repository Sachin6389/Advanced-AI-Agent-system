from langchain_core.messages import (
    HumanMessage,
    SystemMessage
)

from app.agents.llm import llm
from app.tools.search import web_search
from app.mcp.client import MCPResearchClient


async def researcher_agent(
    state: dict
):

    query = state["query"]

    # --------------------------------
    # MCP Research
    # --------------------------------

    mcp_results = ""

    try:

        client = MCPResearchClient()

        mcp_results = await client.search(
            query
        )

    except Exception as exc:

        mcp_results = (
            f"MCP unavailable: {exc}"
        )

    # --------------------------------
    # Tool Calling
    # --------------------------------

    research_llm = llm.bind_tools(
        [web_search]
    )

    prompt = f"""
You are the Research Agent.

Research this request:

{query}

MCP Research:

{mcp_results}

Use web_search if MCP research
is missing or incomplete.

Prefer reliable and recent sources.

Return findings and source URLs.
Do not invent facts.
"""

    response = await research_llm.ainvoke(
        [
            SystemMessage(
                content=(
                    "You are a careful "
                    "research agent."
                )
            ),
            HumanMessage(
                content=prompt
            )
        ]
    )

    tool_results = []

    if response.tool_calls:

        for call in response.tool_calls:

            if (
                call["name"]
                == "web_search"
            ):

                result = (
                    web_search.invoke(
                        call["args"]
                    )
                )

                tool_results.append(
                    result
                )

    parts = [
        mcp_results,
        response.content,
        *tool_results
    ]

    research = "\n\n".join(
        part
        for part in parts
        if part
    )

    return {

        "research": research,

        "sources": extract_sources(
            parts
        ),

        "status":
            "research_completed"

    }


def extract_sources(
    results: list[str]
):

    sources = []

    seen = set()

    for text in results:

        for block in text.split(
            "\n\n"
        ):

            lines = block.splitlines()

            title = next(
                (
                    line[7:]
                    for line in lines
                    if line.startswith(
                        "TITLE: "
                    )
                ),
                ""
            )

            url = next(
                (
                    line[5:]
                    for line in lines
                    if line.startswith(
                        "URL: "
                    )
                ),
                ""
            )

            if url and url not in seen:

                seen.add(url)

                sources.append(
                    {
                        "title": title,
                        "url": url
                    }
                )

    return sources