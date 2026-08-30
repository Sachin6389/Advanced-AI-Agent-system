async def supervisor_agent(state: dict) -> str:
    """
    Supervisor Agent

    Decides which agent should execute next
    based on the current workflow state and
    the user's request.
    """

    query = state.get(
        "query",
        ""
    ).lower()

    # --------------------------------
    # 1. Research
    # --------------------------------

    if not state.get("research"):

        return "researcher"


    # --------------------------------
    # 2. Document requirement
    # --------------------------------

    document_keywords = [
        "document",
        "pdf",
        "file",
        "uploaded",
        "report.pdf",
        "read file",
        "read document",
        "analyze document",
        "from my file",
    ]

    needs_document = any(
        keyword in query
        for keyword in document_keywords
    )

    if (
        needs_document
        and not state.get(
            "document_content"
        )
    ):

        return "document_agent"


    # --------------------------------
    # 3. Analysis
    # --------------------------------

    if not state.get("analysis"):

        return "analyst"


    # --------------------------------
    # 4. Fact Checking
    # --------------------------------

    if not state.get("fact_check"):

        return "fact_checker"


    # --------------------------------
    # 5. Report Generation
    # --------------------------------

    if not state.get("report"):

        return "reporter"


    # --------------------------------
    # 6. Finish
    # --------------------------------

    return "finish"