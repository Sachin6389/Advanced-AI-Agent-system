import os

from mcp.server.fastmcp import (
    FastMCP
)

from tavily import TavilyClient


mcp = FastMCP(
    "Research MCP Server"
)


@mcp.tool()
def search_research(
    query: str
):

    """
    Search the web using Tavily.
    """

    api_key = os.getenv(
        "tavily_api_key"
    )

    if not api_key:

        return (
            "tavily_api_key is not configured."
        )

    client = TavilyClient(
        api_key=api_key
    )

    response = client.search(
        query=query,
        max_results=5
    )

    results = []

    for item in response.get(
        "results",
        []
    ):

        results.append(

            f"""
TITLE: {item.get("title", "")}

URL: {item.get("url", "")}

CONTENT:
{item.get("content", "")}
"""
        )

    return "\n".join(
        results
    )


@mcp.resource(
    "research://about"
)
def research_about():

    return (
        "Research MCP Server exposes "
        "web research as an MCP tool."
    )


if __name__ == "__main__":

    mcp.run(
        transport="stdio"
    )