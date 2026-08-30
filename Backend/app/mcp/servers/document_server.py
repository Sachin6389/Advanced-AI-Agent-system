from pathlib import Path

from mcp.server.fastmcp import (
    FastMCP
)


mcp = FastMCP(
    "Document MCP Server"
)


@mcp.tool()
def list_documents(
    directory: str = "../data/documents"
):

    """
    List available documents.
    """

    path = Path(
        directory
    )

    if not path.exists():

        return []

    return [

        file.name

        for file in path.iterdir()

        if file.is_file()

    ]


@mcp.resource(
    "documents://about"
)
def documents_about():

    return (
        "MCP server for document metadata."
    )


if __name__ == "__main__":

    mcp.run(
        transport="stdio"
    )