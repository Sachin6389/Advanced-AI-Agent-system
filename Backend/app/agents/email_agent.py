
import logging
import re

from app.agents.llm import llm

from app.security.permission import (
    requires_approval,
)

from app.approval.approval_maneger import (
    ApprovalManager,
)

from app.checkpoints.database import (
    CheckpointDB,
)

from app.configuration import (
    settings,
)


# =========================================================
# Logger
# =========================================================

logger = logging.getLogger(
    __name__
)


# =========================================================
# Database
# =========================================================

db = CheckpointDB(
    settings.database_path
)


# =========================================================
# Approval Manager
# =========================================================

approval_manager = ApprovalManager(
    db
)


# =========================================================
# Email Agent
# =========================================================

async def email_agent(
    state: dict,
):
    """
    Email Agent.

    Flow:

        User Request
             |
             v
        Generate Email
             |
             v
        Validate Email
             |
             v
        Create Approval
             |
             v
        Return Draft
             |
             v
        Human Approval
             |
        +----+----+
        |         |
      APPROVE   REJECT
        |         |
        v         v
    Send Tool   Revise Email
    """

    # -----------------------------------------------------
    # Get user query
    # -----------------------------------------------------

    query = state.get(
        "query",
        "",
    ).strip()

    if not query:

        return {
            "status": "email_failed",
            "recipient": None,
            "email_payload": None,
            "approval_required": False,
            "approval_status": None,
            "approval_action": None,
            "approval_reason": None,
            "approval": None,
            "email_sent": False,
            "tool_result": None,
            "errors": [
                "User message is empty."
            ],
        }

    # -----------------------------------------------------
    # Get session ID
    # -----------------------------------------------------

    session_id = state.get(
        "session_id"
    )

    if not session_id:

        return {
            "status": "email_failed",
            "recipient": None,
            "email_payload": None,
            "approval_required": False,
            "approval_status": None,
            "approval_action": None,
            "approval_reason": None,
            "approval": None,
            "email_sent": False,
            "tool_result": None,
            "errors": [
                "Session ID is required "
                "for email approval."
            ],
        }

    # -----------------------------------------------------
    # Check whether approval is required
    # -----------------------------------------------------

    approval_required = requires_approval(
        "send_email"
    )

    # -----------------------------------------------------
    # LLM prompt
    # -----------------------------------------------------

    prompt = f"""
You are an Email Agent.

The user wants to send an email.

Analyze ONLY the user's message below.

USER MESSAGE:

{query}

Your tasks:

1. Identify the recipient email address.
2. Create a concise professional subject.
3. Create a professional email body.

IMPORTANT RULES:

- The recipient MUST come from the user's message.
- Do NOT use recipient information from application state.
- Do NOT invent an email address.
- Do NOT invent facts.
- Do NOT invent names.
- If the user's message does not contain a valid
  email address, return NONE.
- Keep the email professional.
- Keep the body concise.
- Do not mention agents.
- Do not mention workflow.
- Do not mention prompts.
- Do not mention approval.
- Do not say that the email has been sent.

Return ONLY this exact format:

RECIPIENT:
<email address or NONE>

SUBJECT:
<subject>

BODY:
<body>
"""

    # -----------------------------------------------------
    # Call LLM
    # -----------------------------------------------------

    try:

        response = await llm.ainvoke(
            prompt
        )

        content = (
            response.content
            if response.content
            else ""
        ).strip()

    except Exception as exc:

        logger.exception(
            "Email agent LLM failed: %s",
            exc,
        )

        errors = list(
            state.get(
                "errors",
                []
            )
        )

        errors.append(
            f"Email generation failed: {exc}"
        )

        return {
            "status": "email_failed",
            "recipient": None,
            "email_payload": None,
            "approval_required": False,
            "approval_status": None,
            "approval_action": None,
            "approval_reason": None,
            "approval": None,
            "email_sent": False,
            "tool_result": None,
            "errors": errors,
        }

    # -----------------------------------------------------
    # Extract recipient
    # -----------------------------------------------------

    recipient_match = re.search(
        r"RECIPIENT:\s*(.*?)(?=\n\s*SUBJECT:)",
        content,
        re.IGNORECASE | re.DOTALL,
    )

    if not recipient_match:

        return {
            "status": "email_failed",
            "recipient": None,
            "email_payload": None,
            "approval_required": False,
            "approval_status": None,
            "approval_action": None,
            "approval_reason": None,
            "approval": None,
            "email_sent": False,
            "tool_result": None,
            "errors": [
                "LLM did not return "
                "a recipient."
            ],
        }

    recipient = (
        recipient_match
        .group(1)
        .strip()
    )

    # -----------------------------------------------------
    # Validate recipient exists
    # -----------------------------------------------------

    if (
        not recipient
        or recipient.upper() == "NONE"
    ):

        return {
            "status": "email_failed",
            "recipient": None,
            "email_payload": None,
            "approval_required": False,
            "approval_status": None,
            "approval_action": None,
            "approval_reason": None,
            "approval": None,
            "email_sent": False,
            "tool_result": None,
            "errors": [
                "No recipient email address "
                "was found in the user's message."
            ],
        }

    # -----------------------------------------------------
    # Validate email format
    # -----------------------------------------------------

    email_pattern = (
        r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    )

    if not re.match(
        email_pattern,
        recipient,
    ):

        return {
            "status": "email_failed",
            "recipient": None,
            "email_payload": None,
            "approval_required": False,
            "approval_status": None,
            "approval_action": None,
            "approval_reason": None,
            "approval": None,
            "email_sent": False,
            "tool_result": None,
            "errors": [
                f"Invalid recipient email: "
                f"{recipient}"
            ],
        }

    # -----------------------------------------------------
    # Extract subject
    # -----------------------------------------------------

    subject_match = re.search(
        r"SUBJECT:\s*(.*?)(?=\n\s*BODY:)",
        content,
        re.IGNORECASE | re.DOTALL,
    )

    if not subject_match:

        return {
            "status": "email_failed",
            "recipient": recipient,
            "email_payload": None,
            "approval_required": False,
            "approval_status": None,
            "approval_action": None,
            "approval_reason": None,
            "approval": None,
            "email_sent": False,
            "tool_result": None,
            "errors": [
                "LLM did not generate "
                "an email subject."
            ],
        }

    subject = (
        subject_match
        .group(1)
        .strip()
    )

    # -----------------------------------------------------
    # Extract body
    # -----------------------------------------------------

    body_match = re.search(
        r"BODY:\s*(.*)$",
        content,
        re.IGNORECASE | re.DOTALL,
    )

    if not body_match:

        return {
            "status": "email_failed",
            "recipient": recipient,
            "email_payload": None,
            "approval_required": False,
            "approval_status": None,
            "approval_action": None,
            "approval_reason": None,
            "approval": None,
            "email_sent": False,
            "tool_result": None,
            "errors": [
                "LLM did not generate "
                "an email body."
            ],
        }

    body = (
        body_match
        .group(1)
        .strip()
    )

    # -----------------------------------------------------
    # Validate subject
    # -----------------------------------------------------

    if not subject:

        return {
            "status": "email_failed",
            "recipient": recipient,
            "email_payload": None,
            "approval_required": False,
            "approval_status": None,
            "approval_action": None,
            "approval_reason": None,
            "approval": None,
            "email_sent": False,
            "tool_result": None,
            "errors": [
                "Email subject is empty."
            ],
        }

    # -----------------------------------------------------
    # Validate body
    # -----------------------------------------------------

    if not body:

        return {
            "status": "email_failed",
            "recipient": recipient,
            "email_payload": None,
            "approval_required": False,
            "approval_status": None,
            "approval_action": None,
            "approval_reason": None,
            "approval": None,
            "email_sent": False,
            "tool_result": None,
            "errors": [
                "Email body is empty."
            ],
        }

    # -----------------------------------------------------
    # Create email payload
    # -----------------------------------------------------

    email_payload = {

        "recipient": recipient,

        "subject": subject,

        "body": body,
    }

    # -----------------------------------------------------
    # Approval
    # -----------------------------------------------------

    if approval_required:

        try:

            approval = (
                approval_manager.create(

                    session_id=session_id,

                    action="send_email",

                    reason=(
                        "An email has been "
                        "prepared from the "
                        "user's request. "
                        "Human approval is "
                        "required before "
                        "sending."
                    ),

                    payload=email_payload,
                )
            )

        except Exception as exc:

            logger.exception(
                "Failed to create email approval: %s",
                exc,
            )

            return {
                "status": "email_failed",
                "recipient": recipient,
                "email_payload": email_payload,
                "approval_required": True,
                "approval_status": None,
                "approval_action": "send_email",
                "approval_reason": None,
                "approval": None,
                "email_sent": False,
                "tool_result": None,
                "errors": [
                    "Failed to create "
                    f"approval: {exc}"
                ],
            }
        checkpoint_state = dict(state)

        checkpoint_state.update({
          "session_id": session_id,
          "user_id": state.get("user_id"),

          "status": "awaiting_approval",

          "recipient": recipient,

          "email_payload": email_payload,

          "approval_required": True,

          "approval_status": "pending",

          "approval_action": "send_email",

          "approval_reason": (
            "An email has been prepared from "
            "the user's request. Human approval "
            "is required before sending."
         ),

         "approval": approval,

         "email_sent": False,

         "tool_result": None,

         "errors": [],
         })

        try:

         db.save_state(
            session_id=session_id,
            state=checkpoint_state,
         )

         logger.info(
            "Email approval checkpoint saved: session=%s user=%s",
            session_id,
            checkpoint_state.get("user_id"),
         )

        except Exception as exc:

         logger.exception(
            "Failed to save email approval checkpoint: %s",
            exc,
         )

         return {
            "status": "email_failed",
            "recipient": recipient,
            "email_payload": email_payload,
            "approval_required": True,
            "approval_status": "pending",
            "approval_action": "send_email",
            "approval_reason": (
                "Approval was created, but "
                "checkpoint could not be saved."
            ),
            "approval": approval,
            "email_sent": False,
            "tool_result": None,
            "errors": [
                f"Failed to save checkpoint: {exc}"
            ],
         }

        # -------------------------------------------------
        # IMPORTANT:
        # Email is NOT sent here.
        # -------------------------------------------------

        return {

            "status": "awaiting_approval",

            "recipient": recipient,

            "email_payload": email_payload,

            "approval_required": True,

            "approval_status": "pending",

            "approval_action": "send_email",

            "approval_reason": (
                "An email has been "
                "prepared from the "
                "user's request. "
                "Human approval is "
                "required before "
                "sending."
            ),

            "approval": approval,

            "email_sent": False,

            "tool_result": None,

            "errors": [],
        }

    # -----------------------------------------------------
    # Fallback if approval is disabled
    # -----------------------------------------------------

    return {

        "status": "email_ready",

        "recipient": recipient,

        "email_payload": email_payload,

        "approval_required": False,

        "approval_status": "not_required",

        "approval_action": "send_email",

        "approval_reason": None,

        "approval": None,

        "email_sent": False,

        "tool_result": None,

        "errors": [],
    }

