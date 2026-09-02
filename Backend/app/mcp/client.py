import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from mcp import (
    ClientSession,
    StdioServerParameters,
)

from mcp.client.stdio import (
    stdio_client,
)


# ============================================================
# LOGGING
# ============================================================

logger = logging.getLogger(__name__)


# ============================================================
# PATH CONFIGURATION
# ============================================================
#
# Backend/
# │
# └── app/
#     └── mcp/
#         ├── client.py
#         │
#         └── servers/
#             ├── research_server.py
#             └── document_server.py
#
# ============================================================

MCP_DIR = Path(__file__).resolve().parent

APP_DIR = MCP_DIR.parent

BACKEND_DIR = APP_DIR.parent

SERVERS_DIR = MCP_DIR / "servers"


# ============================================================
# ENVIRONMENT FILE
# ============================================================

ENV_FILE = BACKEND_DIR / ".env"


# ============================================================
# LOAD ENVIRONMENT
# ============================================================

load_dotenv(
    dotenv_path=str(ENV_FILE),
    override=False,
)


# ============================================================
# MCP CLIENT
# ============================================================

class MCPResearchClient:

    # ========================================================
    # ENVIRONMENT
    # ========================================================

    @staticmethod
    def get_environment() -> dict[str, str]:
        """
        Build the environment for the MCP subprocess.
        """

        # ----------------------------------------------------
        # Copy parent environment
        # ----------------------------------------------------

        env = os.environ.copy()

        # ----------------------------------------------------
        # Tavily API key
        # ----------------------------------------------------

        tavily_api_key = (
            os.getenv("TAVILY_API_KEY")
            or os.getenv("tavily_api_key")
        )

        if tavily_api_key:

            tavily_api_key = tavily_api_key.strip()

            # Standard name
            env["TAVILY_API_KEY"] = (
                tavily_api_key
            )

            # Backward-compatible name
            env["tavily_api_key"] = (
                tavily_api_key
            )

        # ----------------------------------------------------
        # Python configuration
        # ----------------------------------------------------

        env["PYTHONUNBUFFERED"] = "1"

        # ----------------------------------------------------
        # PYTHONPATH
        # ----------------------------------------------------

        existing_pythonpath = (
            env.get("PYTHONPATH", "")
        )

        if existing_pythonpath:

            env["PYTHONPATH"] = (
                str(BACKEND_DIR)
                + os.pathsep
                + existing_pythonpath
            )

        else:

            env["PYTHONPATH"] = (
                str(BACKEND_DIR)
            )

        return env

    # ========================================================
    # RESEARCH SERVER PARAMETERS
    # ========================================================

    @classmethod
    def research_server_params(
        cls,
    ) -> StdioServerParameters:
        """
        Create parameters for research_server.py.
        """

        server_path = (
            SERVERS_DIR
            / "research_server.py"
        )

        # ----------------------------------------------------
        # Validate server path
        # ----------------------------------------------------

        if not server_path.exists():

            raise FileNotFoundError(
                "Research MCP server not found:\n"
                f"{server_path}"
            )

        if not server_path.is_file():

            raise FileNotFoundError(
                "Research MCP server path is not a file:\n"
                f"{server_path}"
            )

        # ----------------------------------------------------
        # Logging
        # ----------------------------------------------------

        logger.info(
            "Research MCP server path: %s",
            server_path,
        )

        logger.info(
            "Research MCP Python: %s",
            sys.executable,
        )

        logger.info(
            "Research MCP working directory: %s",
            BACKEND_DIR,
        )

        logger.info(
            "Research MCP .env: %s",
            ENV_FILE,
        )

        logger.info(
            "Research MCP .env exists: %s",
            ENV_FILE.exists(),
        )

        # ----------------------------------------------------
        # Environment
        # ----------------------------------------------------

        env = cls.get_environment()

        if env.get("TAVILY_API_KEY"):

            logger.info(
                "Tavily API key passed to MCP process"
            )

        else:

            logger.warning(
                "Tavily API key was NOT found"
            )

        # ----------------------------------------------------
        # Return parameters
        # ----------------------------------------------------

        return StdioServerParameters(

            command=sys.executable,

            args=[
                "-u",
                str(server_path),
            ],

            env=env,

            cwd=str(BACKEND_DIR),
        )

    # ========================================================
    # DOCUMENT SERVER PARAMETERS
    # ========================================================

    @classmethod
    def document_server_params(
        cls,
    ) -> StdioServerParameters:
        """
        Create parameters for document_server.py.
        """

        server_path = (
            SERVERS_DIR
            / "document_server.py"
        )

        # ----------------------------------------------------
        # Validate
        # ----------------------------------------------------

        if not server_path.exists():

            raise FileNotFoundError(
                "Document MCP server not found:\n"
                f"{server_path}"
            )

        if not server_path.is_file():

            raise FileNotFoundError(
                "Document MCP server path is not a file:\n"
                f"{server_path}"
            )

        # ----------------------------------------------------
        # Logging
        # ----------------------------------------------------

        logger.info(
            "Document MCP server path: %s",
            server_path,
        )

        logger.info(
            "Document MCP Python: %s",
            sys.executable,
        )

        logger.info(
            "Document MCP working directory: %s",
            BACKEND_DIR,
        )

        # ----------------------------------------------------
        # Environment
        # ----------------------------------------------------

        env = cls.get_environment()

        # ----------------------------------------------------
        # Parameters
        # ----------------------------------------------------

        return StdioServerParameters(

            command=sys.executable,

            args=[
                "-u",
                str(server_path),
            ],

            env=env,

            cwd=str(BACKEND_DIR),
        )

    # ========================================================
    # EXTRACT TEXT
    # ========================================================

    @staticmethod
    def extract_text(
        result,
    ) -> str:
        """
        Extract text content from an MCP tool result.
        """

        output = []

        content = getattr(
            result,
            "content",
            None,
        )

        if not content:

            return ""

        for item in content:

            text = getattr(
                item,
                "text",
                None,
            )

            if text:

                output.append(
                    str(text)
                )

        return "\n\n".join(
            output
        ).strip()

    # ========================================================
    # SEARCH
    # ========================================================

    async def search(
        self,
        query: str,
    ) -> str:
        """
        Execute the search_research MCP tool.
        """

        # ----------------------------------------------------
        # Validate query
        # ----------------------------------------------------

        if query is None:

            return ""

        if not isinstance(
            query,
            str,
        ):

            raise TypeError(
                "Research query must be a string."
            )

        query = query.strip()

        if not query:

            return ""

        # ----------------------------------------------------
        # Logging
        # ----------------------------------------------------

        logger.info(
            "Starting Research MCP"
        )

        logger.info(
            "Research query: %s",
            query,
        )

        # ----------------------------------------------------
        # Server parameters
        # ----------------------------------------------------

        params = (
            self.research_server_params()
        )

        try:

            logger.info(
                "Starting Research MCP subprocess..."
            )

            # =================================================
            # IMPORTANT WINDOWS FIX
            # =================================================
            #
            # DO NOT use:
            #
            #     io.StringIO()
            #
            # for errlog.
            #
            # Windows subprocess requires an object with
            # a real fileno().
            #
            # sys.stderr provides that.
            #
            # =================================================

            async with stdio_client(
                params,
                errlog=sys.stderr,
            ) as (
                read,
                write,
            ):

                logger.info(
                    "Research MCP stdio connection established"
                )

                # --------------------------------------------
                # MCP session
                # --------------------------------------------

                async with ClientSession(
                    read,
                    write,
                ) as session:

                    logger.info(
                        "Initializing Research MCP session..."
                    )

                    # ----------------------------------------
                    # MCP initialization
                    # ----------------------------------------

                    await session.initialize()

                    logger.info(
                        "Research MCP session initialized successfully"
                    )

                    # ----------------------------------------
                    # Get available tools
                    # ----------------------------------------

                    logger.info(
                        "Checking Research MCP tools..."
                    )

                    tools_result = (
                        await session.list_tools()
                    )

                    tool_names = [
                        tool.name
                        for tool in tools_result.tools
                    ]

                    logger.info(
                        "Research MCP tools: %s",
                        tool_names,
                    )

                    # ----------------------------------------
                    # Validate tool
                    # ----------------------------------------

                    if (
                        "search_research"
                        not in tool_names
                    ):

                        raise RuntimeError(
                            "Research MCP started successfully "
                            "but 'search_research' tool was "
                            "not registered."
                        )

                    # ----------------------------------------
                    # Call research tool
                    # ----------------------------------------

                    logger.info(
                        "Calling MCP tool: search_research"
                    )

                    result = (
                        await session.call_tool(
                            "search_research",
                            {
                                "query": query,
                            },
                        )
                    )

                    # ----------------------------------------
                    # Check MCP tool error
                    # ----------------------------------------

                    if getattr(
                        result,
                        "is_error",
                        False,
                    ):

                        logger.error(
                            "Research MCP tool returned an error."
                        )

                    # ----------------------------------------
                    # Extract response
                    # ----------------------------------------

                    final_output = (
                        self.extract_text(
                            result
                        )
                    )

                    if not final_output:

                        logger.warning(
                            "Research MCP returned no text."
                        )

                        return (
                            "Research MCP returned no results."
                        )

                    logger.info(
                        "Research MCP completed successfully"
                    )

                    return final_output

        except Exception as exc:

            logger.exception(
                "Research MCP failed: %s",
                exc,
            )

            # ------------------------------------------------
            # IMPORTANT:
            #
            # Do not swallow the exception.
            # The researcher should know that MCP failed.
            # ------------------------------------------------

            raise RuntimeError(
                f"Research MCP failed: {exc}"
            ) from exc

    # ========================================================
    # DOCUMENTS
    # ========================================================

    async def documents(self):
        """
        Execute the list_documents MCP tool.
        """

        logger.info(
            "Starting Document MCP"
        )

        params = (
            self.document_server_params()
        )

        try:

            logger.info(
                "Starting Document MCP subprocess..."
            )

            # ------------------------------------------------
            # Same Windows fix:
            # use sys.stderr, NOT StringIO
            # ------------------------------------------------

            async with stdio_client(
                params,
                errlog=sys.stderr,
            ) as (
                read,
                write,
            ):

                logger.info(
                    "Document MCP stdio connection established"
                )

                # --------------------------------------------
                # MCP session
                # --------------------------------------------

                async with ClientSession(
                    read,
                    write,
                ) as session:

                    logger.info(
                        "Initializing Document MCP session..."
                    )

                    await session.initialize()

                    logger.info(
                        "Document MCP session initialized successfully"
                    )

                    # ----------------------------------------
                    # Get tools
                    # ----------------------------------------

                    tools_result = (
                        await session.list_tools()
                    )

                    tool_names = [
                        tool.name
                        for tool in tools_result.tools
                    ]

                    logger.info(
                        "Document MCP tools: %s",
                        tool_names,
                    )

                    # ----------------------------------------
                    # Validate tool
                    # ----------------------------------------

                    if (
                        "list_documents"
                        not in tool_names
                    ):

                        raise RuntimeError(
                            "Document MCP started successfully "
                            "but 'list_documents' tool was "
                            "not registered."
                        )

                    # ----------------------------------------
                    # Call tool
                    # ----------------------------------------

                    result = (
                        await session.call_tool(
                            "list_documents",
                            {},
                        )
                    )

                    logger.info(
                        "Document MCP completed successfully"
                    )

                    return result

        except Exception as exc:

            logger.exception(
                "Document MCP failed: %s",
                exc,
            )

            raise RuntimeError(
                f"Document MCP failed: {exc}"
            ) from exc