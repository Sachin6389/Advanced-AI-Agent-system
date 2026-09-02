import logging

from app.approval.approval_maneger import (
    ApprovalManager,
)

from app.checkpoints.database import (
    CheckpointDB,
)

from app.configuration import (
    settings,
)

from app.tools.emails import (
    send_email_tool,
)


logger = logging.getLogger(
    __name__
)


db = CheckpointDB(
    settings.database_path
)


approval_manager = ApprovalManager(
    db
)


async def execute_approved_email(
    session_id: str,
):
    """
    Execute email ONLY after approval.

    DB approval is the source of truth.
    """

    # =====================================================
    # 1. Get approval from DB
    # =====================================================

    approval = approval_manager.get(
        session_id
    )

    if not approval:

        raise ValueError(
            "Approval not found."
        )

    # =====================================================
    # 2. Verify approval
    # =====================================================

    if approval["status"] != "approved":

        raise PermissionError(
            "Email has not been approved."
        )

    # =====================================================
    # 3. Verify action
    # =====================================================

    if approval["action"] != "send_email":

        raise ValueError(
            "Invalid approval action."
        )

    # =====================================================
    # 4. Get approved payload FROM DB
    # =====================================================

    payload = approval.get(
        "payload"
    )

    if not payload:

        raise ValueError(
            "Approved email payload is missing."
        )

    recipient = payload.get(
        "recipient"
    )

    subject = payload.get(
        "subject"
    )

    body = payload.get(
        "body"
    )

    if not recipient:
        raise ValueError(
            "Recipient is missing."
        )

    if not subject:
        raise ValueError(
            "Subject is missing."
        )

    if not body:
        raise ValueError(
            "Body is missing."
        )

    # =====================================================
    # 5. SEND EMAIL
    # =====================================================

    try:

        result = await send_email_tool(
            recipient=recipient,
            subject=subject,
            body=body,
        )

    except Exception as exc:

        logger.exception(
            "Email sending failed: %s",
            exc,
        )

        raise

    # =====================================================
    # 6. Return result
    # =====================================================

    return {
        "status": "email_sent",
        "email_sent": True,
        "tool_result": result,
        "recipient": recipient,
        "subject": subject,
    }