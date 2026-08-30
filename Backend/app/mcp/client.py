import sys

from pathlib import Path

from mcp import (
    ClientSession,
    StdioServerParameters
)

from mcp.client.stdio import (
    stdio_client
)


class MCPResearchClient:

    async def search(
        self,
        query: str
    ):

        server_path = (
            Path(__file__).parent
            / "servers"
            / "research_server.py"
        )

        params = StdioServerParameters(

            command=sys.executable,

            args=[
                str(server_path)
            ]

        )

        async with stdio_client(
            params
        ) as (
            read,
            write
        ):

            async with ClientSession(
                read,
                write
            ) as session:

                await session.initialize()

                result = (
                    await session.call_tool(
                        "search_research",
                        {
                            "query": query
                        }
                    )
                )

                output = []

                for content in result.content:

                    text = getattr(
                        content,
                        "text",
                        None
                    )

                    if text:

                        output.append(
                            text
                        )

                return "\n".join(
                    output
                )