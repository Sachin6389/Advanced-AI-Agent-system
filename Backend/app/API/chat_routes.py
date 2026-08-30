from pathlib import Path

from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from app.schemas.chat import (
    ChatRequest,
    ChatResponse
)

from app.security.auth import (
    get_current_user
)

from app.security.permission import (
    requires_approval
)

from app.checkpoints.database import (
    CheckpointDB
)

from app.approval.approval_maneger import (
    ApprovalManager
)

from app.configuration import (
    settings
)

from app.workflows.research_graph import (
    build_graph
)


router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)


db = CheckpointDB(
    settings.database_path
)

approval_manager = ApprovalManager(
    db
)


@router.post(
    "",
    response_model=ChatResponse
)
async def chat(

    request: ChatRequest,

    current_user=Depends(
        get_current_user
    )

):

    if (
        current_user["user_id"]
        != request.user_id
    ):

        raise HTTPException(
            status_code=403,
            detail="User mismatch"
        )


    Path(
        settings.reports_dir
    ).mkdir(
        parents=True,
        exist_ok=True
    )


    Path(
        settings.documents_dir
    ).mkdir(
        parents=True,
        exist_ok=True
    )


    existing = db.load_state(
        request.session_id
    )


    if (
        existing
        and existing.get("status")
        == "awaiting_approval"
    ):

        raise HTTPException(
            status_code=409,
            detail=(
                "Session is waiting "
                "for human approval."
            )
        )


    state = {

        "user_id":
            request.user_id,

        "user_role":
            current_user["role"],

        "session_id":
            request.session_id,

        "query":
            request.message,

        "recipient":
            request.recipient,

        "messages":
            existing.get(
                "messages",
                []
            )
            if existing
            else [],

        "memories":
            existing.get(
                "memories",
                []
            )
            if existing
            else [],

        "previous_queries":
            existing.get(
                "previous_queries",
                []
            )
            if existing
            else [],

        "errors": [],

        "retry_count": 0,

        "status": "started"

    }


    try:

        graph = build_graph()

        result = await graph.ainvoke(
            state
        )


        # -------------------------
        # Sensitive action detection
        # -------------------------

        message = (
            request.message.lower()
        )


        wants_email = any(

            phrase in message

            for phrase in [

                "send email",

                "email the report",

                "email report"

            ]

        )


        wants_publish = any(

            phrase in message

            for phrase in [

                "publish report",

                "publish the report"

            ]

        )


        if (
            result.get("report")
            and (
                wants_email
                or wants_publish
            )
        ):

            action = (

                "send_email"

                if wants_email

                else

                "publish_report"

            )


            if not requires_approval(
                action
            ):

                raise HTTPException(
                    status_code=500,
                    detail=(
                        "Approval policy "
                        "misconfigured."
                    )
                )


            if (
                action == "send_email"
                and not request.recipient
            ):

                raise HTTPException(
                    status_code=400,
                    detail=(
                        "recipient is required "
                        "for email."
                    )
                )


            if action == "send_email":

                payload = {

                    "recipient":
                        request.recipient,

                    "subject":
                        "AI Research Agent Report",

                    "body":
                        result["report"]

                }

            else:

                payload = {

                    "title":
                        "AI Research Agent Report",

                    "body":
                        result["report"]

                }


            approval = (
                approval_manager.create(

                    request.session_id,

                    action,

                    (
                        "The agent wants to "
                        f"perform sensitive action: "
                        f"{action}"
                    ),

                    payload

                )
            )


            result[
                "approval_required"
            ] = True


            result[
                "approval_status"
            ] = "pending"


            result[
                "approval_action"
            ] = action


            result[
                "approval_reason"
            ] = approval[
                "reason"
            ]


            result[
                "status"
            ] = "awaiting_approval"


        result.setdefault(
            "previous_queries",
            []
        ).append(
            request.message
        )


        db.save_state(
            request.session_id,
            result
        )


        return ChatResponse(

            session_id=
                request.session_id,

            status=
                result.get(
                    "status",
                    "completed"
                ),

            answer=
                result.get(
                    "report"
                ),

            plan=
                result.get(
                    "plan",
                    []
                ),

            sources=
                result.get(
                    "sources",
                    []
                ),

            approval_required=
                result.get(
                    "approval_required",
                    False
                ),

            approval=
                approval_manager.get(
                    request.session_id
                ),

            errors=
                result.get(
                    "errors",
                    []
                )

        )


    except HTTPException:

        raise


    except Exception as exc:

        state.setdefault(
            "errors",
            []
        ).append(
            str(exc)
        )

        state[
            "status"
        ] = "failed"


        db.save_state(
            request.session_id,
            state
        )


        return ChatResponse(

            session_id=
                request.session_id,

            status="failed",

            errors=
                state["errors"]

        )