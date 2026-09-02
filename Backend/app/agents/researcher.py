
import logging

from langchain_core.messages import (
    HumanMessage,
    SystemMessage,
)

from app.mcp.client import MCPResearchClient


logger = logging.getLogger(__name__)


async def researcher_agent(
    state: dict,
):

    query = state.get(
        "query",
        "",
    ).strip()

    if not query:

        return {
            "research": "",
            "sources": [],
            "messages": [],
            "status": "research_failed",
            "error": "Query is empty.",
        }

    # ============================================================
    # MESSAGE HISTORY
    # ============================================================

    messages = list(
        state.get(
            "messages",
            [],
        )
    )

    # Save user message
    messages.append(
        HumanMessage(
            content=query
        )
    )

    # ============================================================
    # MCP RESEARCH
    # ============================================================

    mcp_results = ""

    try:

        logger.info(
            "Starting Research MCP"
        )

        client = MCPResearchClient()

        mcp_results = await client.search(
            query
        )

        logger.info(
            "Research MCP completed successfully"
        )

    except Exception as exc:

        logger.exception(
            "Research MCP failed: %s",
            exc,
        )

        return {
            "research": "",
            "sources": [],
            "messages": messages,
            "status": "research_failed",
            "error": f"MCP unavailable: {exc}",
        }

    # ============================================================
    # VALIDATE MCP RESULT
    # ============================================================

    if not mcp_results:

        logger.warning(
            "Research MCP returned empty result"
        )

        return {
            "research": "",
            "sources": [],
            "messages": messages,
            "status": "research_failed",
            "error": "Research MCP returned no results.",
        }

    # ============================================================
    # SAVE MCP RESULT AS ASSISTANT MESSAGE
    # ============================================================

    messages.append(
        SystemMessage(
            content=(
                "Research result retrieved from "
                "the Research MCP server."
            )
        )
    )

    messages.append(
        HumanMessage(
            content=mcp_results
        )
    )

    # ============================================================
    # EXTRACT SOURCES
    # ============================================================

    sources = extract_sources(
        [mcp_results]
    )

    # ============================================================
    # FINAL RESEARCH
    # ============================================================

    research = mcp_results

    logger.info(
        "Research completed with %s sources",
        len(sources),
    )

    return {
        "research": research,
        "sources": sources,
        "status": "research_completed",
    }


# ================================================================
# SOURCE EXTRACTION
# ================================================================

def extract_sources(
    results: list[str],
):
    """
    Extract TITLE and URL blocks from MCP results.

    Expected MCP format:

    TITLE: Example Article
    URL: https://example.com
    """

    sources = []

    seen = set()

    for text in results:

        if not text:
            continue

        for block in text.split(
            "\n\n"
        ):

            lines = block.splitlines()

            title = next(
                (
                    line[7:].strip()
                    for line in lines
                    if line.startswith(
                        "TITLE: "
                    )
                ),
                "",
            )

            url = next(
                (
                    line[5:].strip()
                    for line in lines
                    if line.startswith(
                        "URL: "
                    )
                ),
                "",
            )

            if url and url not in seen:

                seen.add(url)

                sources.append(
                    {
                        "title": title,
                        "url": url,
                    }
                )

    return sources

