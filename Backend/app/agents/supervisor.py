
import logging


logger = logging.getLogger(__name__)


async def supervisor_agent(
    state: dict,
) -> str:
    """
    Supervisor Agent.

    The supervisor only decides between three
    top-level workflow routes:

        1. planner
        2. document
        3. send_email

    Research, analysis, fact-checking and reporting
    are handled internally by the planner pipeline.

    Human approval is NOT handled inside the graph.
    The API layer handles approval for sensitive actions.
    """

    query = state.get(
        "query",
        "",
    ).lower().strip()

    # ============================================================
    # 1. DOCUMENT REQUEST
    # ============================================================

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
        and not state.get("file_path")
    ):

        logger.info(
            "Supervisor selected: document"
        )

        return "document"

    # ============================================================
    # 2. EMAIL REQUEST
    # ============================================================

    email_phrases = [
        "send email",
        "send an email",
        "email the report",
        "email report",
        "send report by email",
        "send research by email",
        "mail the report",
        "email this report",
    ]

    needs_email = any(
        phrase in query
        for phrase in email_phrases
    )

    if needs_email:

        logger.info(
            "Supervisor selected: send_email"
        )

        return "send_email"

    # ============================================================
    # 3. DEFAULT → PLANNER
    # ============================================================

    logger.info(
        "Supervisor selected: planner"
    )

    return "planner"

