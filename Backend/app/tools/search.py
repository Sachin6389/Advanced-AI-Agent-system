from langchain_core.tools import tool
from tavily import TavilyClient

from app.configuration import settings


client = TavilyClient(
    api_key=settings.tavily_api_key
)


@tool
def web_search(query: str) -> str:
    """
    Search the web for current information.
    """

    response = client.search(
        query=query,
        max_results=5
    )

    results = response.get(
        "results",
        []
    )

    if not results:

        return "No search results found."

    output = []

    for result in results:

        output.append(
            f"""
TITLE: {result.get("title", "")}

URL: {result.get("url", "")}

CONTENT:
{result.get("content", "")}
"""
        )

    return "\n".join(output)