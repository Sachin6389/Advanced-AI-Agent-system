from pathlib import Path

from langchain_core.tools import tool

from app.configuration import (
    settings
)


@tool
def read_document(
    file_name: str
):

    """
    Read a local document.
    """

    base = Path(
        settings.documents_dir
    ).resolve()

    path = (
        base / file_name
    ).resolve()


    if base not in path.parents:

        raise ValueError(
            "Invalid document path"
        )


    if not path.exists():

        raise FileNotFoundError(
            f"Document not found: "
            f"{file_name}"
        )


    return path.read_text(
        encoding="utf-8",
        errors="ignore"
    )[:50000]