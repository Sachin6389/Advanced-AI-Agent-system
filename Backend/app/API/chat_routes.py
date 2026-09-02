import logging

from fastapi import APIRouter, HTTPException

from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
)

from app.workflows.research_graph import (
    build_graph,
)


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)


# ============================================================
# GRAPH
# ============================================================

graph = build_graph()


# ============================================================
# CHAT
# ============================================================

@router.post(
        "",
    response_model=ChatResponse,
)
async def chat(
    request: ChatRequest,
):
    """
    Main AI Agent endpoint.

    Flow:

        Client
          |
          v
        FastAPI
          |
          v
        AgentState
          |
          v
        LangGraph
          |
          v
        Supervisor
          |
        +---------+----------+
        |         |          |
      Planner  Document    Email
        |         |          |
      Research    |       Email Draft
        |         |          |
      Analysis    |       Approval
        |         |          |
      Fact Check  |       Return
        |         |
      Reporter   |
        |         |
        +-----> Finish
                  |
                  v
                API
                  |
                  v
              ChatResponse

    IMPORTANT:
    The API does NOT perform approval logic.

    Approval creation, if required, is handled by
    the email agent / workflow.
    """

    # --------------------------------------------------------
    # Validate request
    # --------------------------------------------------------

    if not request.message.strip():
        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty.",
        )

    try:

        # ----------------------------------------------------
        # Build initial AgentState
        # ----------------------------------------------------

        initial_state = {
            "user_id": request.user_id,
            "session_id": request.session_id,

            "query": request.message.strip(),

            # Workflow defaults
            "status": "started",
            "next_agent": None,

            # Planning
            "plan": [],
            "current_step": 0,

            # Agent outputs
            "research": "",
            "analysis": "",
            "fact_check": "",
            "report": "",

            # Sources
            "sources": [],

            # Memory
            "messages": [],
            "memories": [],
            "previous_queries": [],

            # Errors
            "errors": [],
            "retry_count": 0,

            # Document
            "file_path": None,

            # Email
            "email_payload": None,
            "email_subject": None,
            "email_body": None,
            "email_sent": False,

            # Tool
            "tool_result": None,

            # Approval state
            #
            # These are initialized only as state fields.
            # The API does NOT create or process approval.
            "approval_required": False,
            "approval_status": None,
            "approval_action": None,
            "approval_reason": None,
            "approval": None,
        }

        # ----------------------------------------------------
        # Run LangGraph
        # ----------------------------------------------------

        logger.info(
            "Starting workflow | user=%s session=%s",
            request.user_id,
            request.session_id,
        )

        result = await graph.ainvoke(
            initial_state
        )

        logger.info(
            "Workflow completed | user=%s session=%s status=%s",
            request.user_id,
            request.session_id,
            result.get("status"),
        )

        # ----------------------------------------------------
        # Determine answer
        # ----------------------------------------------------

        status = result.get(
            "status",
            "completed",
        )

        errors = result.get(
            "errors",
            [],
        )

        # ----------------------------------------------------
        # Report / document / email response
        # ----------------------------------------------------

        answer = None

        if result.get("report"):
            answer = result["report"]

        elif result.get("email_payload"):
            email_payload = result["email_payload"]

            answer = (
                "Email draft prepared.\n\n"
                f"Recipient: "
                f"{email_payload.get('recipient', '')}\n\n"
                f"Subject: "
                f"{email_payload.get('subject', '')}\n\n"
                f"Body:\n"
                f"{email_payload.get('body', '')}"
            )

        elif result.get("tool_result"):
            answer = str(
                result["tool_result"]
            )

        elif errors:
            answer = errors[-1]

        # ----------------------------------------------------
        # Return API response
        # ----------------------------------------------------

        return ChatResponse(

            session_id=request.session_id,

            status=status,

            answer=answer,

            plan=result.get(
                "plan",
                [],
            ),

            sources=result.get(
                "sources",
                [],
            ),

            approval_required=result.get(
                "approval_required",
                False,
            ),

            approval=result.get(
                "approval"
            ),

            errors=errors,
        )

    except Exception as exc:

        logger.exception(
            "Chat workflow failed | user=%s session=%s",
            request.user_id,
            request.session_id,
        )

        raise HTTPException(
            status_code=500,
            detail="AI workflow execution failed.",
        ) from exc