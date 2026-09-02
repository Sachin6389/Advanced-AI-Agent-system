import logging
import os
import sys
from pathlib import Path


from dotenv import load_dotenv
from tavily import TavilyClient
from mcp.server.fastmcp import FastMCP


# ============================================================
# PATH CONFIGURATION
# ============================================================

SERVER_DIR = Path(__file__).resolve().parent
MCP_DIR = SERVER_DIR.parent
APP_DIR = MCP_DIR.parent
BACKEND_DIR = APP_DIR.parent

ENV_FILE = BACKEND_DIR / ".env"


# ============================================================
# LOAD ENVIRONMENT
# ============================================================

load_dotenv(
    dotenv_path=str(ENV_FILE),
    override=False,
)


# ============================================================
# LOGGING
# ============================================================
#
# CRITICAL:
#
# MCP stdio uses STDOUT for JSON-RPC.
#
# NEVER:
#
#     print(...)
#
# inside this server.
#
# All logs go to STDERR.
#
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    stream=sys.stderr,
    format=(
        "%(asctime)s | "
        "%(levelname)s | "
        "%(name)s | "
        "%(message)s"
    ),
    force=True,
)


logger = logging.getLogger(
    "research_mcp_server"
)


# ============================================================
# STARTUP LOGGING
# ============================================================

logger.info(
    "=========================================="
)

logger.info(
    "Starting Research MCP Server"
)

logger.info(
    "=========================================="
)

logger.info(
    "Python executable: %s",
    sys.executable,
)

logger.info(
    "Python version: %s",
    sys.version.replace("\n", " "),
)

logger.info(
    "Server directory: %s",
    SERVER_DIR,
)

logger.info(
    "Backend directory: %s",
    BACKEND_DIR,
)

logger.info(
    "Environment file: %s",
    ENV_FILE,
)

logger.info(
    "Environment exists: %s",
    ENV_FILE.exists(),
)


# ============================================================
# TAVILY API KEY
# ============================================================

def get_tavily_api_key() -> str | None:
    """
    Get Tavily API key from environment.

    Supports:

        TAVILY_API_KEY

    and:

        tavily_api_key
    """

    api_key = (
        os.getenv("TAVILY_API_KEY")
        or os.getenv("tavily_api_key")
    )

    if api_key:
        api_key = api_key.strip()

    return api_key or None


# ============================================================
# FASTMCP
# ============================================================

mcp = FastMCP(
    name="Research MCP Server",
)


# ============================================================
# SEARCH TOOL
# ============================================================

@mcp.tool()
def search_research(
    query: str,
) -> str:
    """
    Search the web using Tavily.
    """

    logger.info(
        "Received research query: %r",
        query,
    )

    # --------------------------------------------------------
    # Validate query
    # --------------------------------------------------------

    if not isinstance(
        query,
        str,
    ):

        return (
            "Search query must be a string."
        )

    query = query.strip()

    if not query:

        return (
            "Search query cannot be empty."
        )

    # --------------------------------------------------------
    # Get API key
    # --------------------------------------------------------

    api_key = get_tavily_api_key()

    if not api_key:

        logger.error(
            "Tavily API key is missing."
        )

        logger.error(
            "Expected TAVILY_API_KEY or "
            "tavily_api_key in: %s",
            ENV_FILE,
        )

        return (
            "Tavily API key is not configured. "
            "Set TAVILY_API_KEY in Backend/.env."
        )

    logger.info(
        "Tavily API key found."
    )

    # --------------------------------------------------------
    # Create Tavily client
    # --------------------------------------------------------

    try:

        client = TavilyClient(
            api_key=api_key,
        )

    except Exception as exc:

        logger.exception(
            "Failed to initialize Tavily client."
        )

        return (
            "Failed to initialize Tavily client: "
            f"{exc}"
        )

    # --------------------------------------------------------
    # Execute search
    # --------------------------------------------------------

    try:

        response = client.search(
            query=query,
            max_results=3,
        )

    except Exception as exc:

        logger.exception(
            "Tavily search failed."
        )

        return (
            "Tavily search failed: "
            f"{exc}"
        )

    # --------------------------------------------------------
    # Validate response
    # --------------------------------------------------------

    if not isinstance(
        response,
        dict,
    ):

        logger.error(
            "Unexpected Tavily response type: %s",
            type(response).__name__,
        )

        return (
            "Tavily returned an unexpected response."
        )

    # --------------------------------------------------------
    # Extract results
    # --------------------------------------------------------

    results = response.get(
        "results",
        [],
    )

    if not results:

        logger.info(
            "Tavily returned no results."
        )

        return (
            "No search results found."
        )

    # --------------------------------------------------------
    # Format results
    # --------------------------------------------------------

    output: list[str] = []

    for index, item in enumerate(
        results,
        start=1,
    ):

        if not isinstance(
            item,
            dict,
        ):

            continue

        title = item.get(
            "title",
            "Untitled",
        )

        url = item.get(
            "url",
            "",
        )

        content = item.get(
            "content",
            "",
        )

        output.append(
            (
                f"RESULT {index}\n"
                f"TITLE: {title}\n"
                f"URL: {url}\n"
                f"CONTENT:\n{content}"
            )
        )

        logger.info(
            "Result %d: %s",
            index,
            title,
        )

    if not output:

        return (
            "Tavily returned no usable results."
        )

    final_result = (
        "\n\n".join(output)
    )

    logger.info(
        "Research completed successfully. "
        "Results=%d",
        len(output),
    )

    return final_result


# ============================================================
# RESOURCE
# ============================================================

@mcp.resource(
    "research://about",
)
def research_about() -> str:
    """
    Information about the Research MCP server.
    """

    return (
        "Research MCP Server exposes "
        "web research using Tavily."
    )


# ============================================================
# MAIN
# ============================================================

def main() -> None:

    logger.info(
        "Launching Research MCP using stdio transport..."
    )

    try:

        mcp.run(
            transport="stdio",
        )

    except KeyboardInterrupt:

        logger.info(
            "Research MCP server stopped."
        )

    except Exception:

        logger.exception(
            "Research MCP server crashed."
        )

        raise


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()