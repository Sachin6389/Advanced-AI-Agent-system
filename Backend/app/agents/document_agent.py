from langchain_core.messages import HumanMessage

from app.agents.llm import llm
from app.tools.document import read_document


async def document_agent(state: dict) -> dict:

    query = state["query"]

    document_llm = llm.bind_tools(
        [read_document]
    )

    prompt = f"""
You are the Document Agent.

The user wants:

{query}

If the request requires information
from a local document, use the
read_document tool.

Do not invent document contents.
"""

    response = await document_llm.ainvoke(
        [
            HumanMessage(
                content=prompt
            )
        ]
    )

    document_content = ""

    if response.tool_calls:

        for call in response.tool_calls:

            if call["name"] == "read_document":

                document_content = (
                    read_document.invoke(
                        call["args"]
                    )
                )

    return {
        "document_content": document_content,
        "status": "document_completed"
    }