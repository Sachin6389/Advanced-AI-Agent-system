from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from app.schemas.approval import (
    ApprovalDecision
)

from app.security.auth import (
    get_current_user
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

from app.tools.emails import (
    send_email,
    publish_report
)


router = APIRouter(
    prefix="/approval",
    tags=["Human Approval"]
)


db = CheckpointDB(
    settings.database_path
)

manager = ApprovalManager(
    db
)


@router.get(
    "/{session_id}"
)
async def get_approval(

    session_id: str,

    current_user=Depends(
        get_current_user
    )

):

    state = db.load_state(
        session_id
    )

    if (
        not state
        or state.get("user_id")
        != current_user["user_id"]
    ):

        raise HTTPException(
            status_code=404,
            detail="Session not found"
        )


    return (
        manager.get(
            session_id
        )
        or
        {
            "status": "none"
        }
    )


@router.post(
    "/{session_id}"
)
async def decide(

    session_id: str,

    decision: ApprovalDecision,

    current_user=Depends(
        get_current_user
    )

):

    state = db.load_state(
        session_id
    )

    if (
        not state
        or state.get("user_id")
        != current_user["user_id"]
    ):

        raise HTTPException(
            status_code=404,
            detail="Session not found"
        )


    approval = manager.get(
        session_id
    )


    if (
        not approval
        or approval.get("status")
        != "pending"
    ):

        raise HTTPException(
            status_code=409,
            detail=(
                "No pending approval"
            )
        )


    approval = manager.decide(

        session_id,

        decision.approved,

        decision.comment

    )


    if not decision.approved:

        state[
            "approval_status"
        ] = "rejected"

        state[
            "status"
        ] = "completed"

        state[
            "report"
        ] = (
            state.get(
                "report",
                ""
            )
            +
            "\n\n"
            "[Human approval rejected "
            "the sensitive action.]"
        )

        db.save_state(
            session_id,
            state
        )

        return {

            "status": "rejected",

            "session_id":
                session_id

        }


    action = approval[
        "action"
    ]

    payload = approval[
        "payload"
    ]


    try:

        if action == "send_email":

            result = send_email.invoke(
                payload
            )

        elif action == "publish_report":

            result = (
                publish_report.invoke(
                    payload
                )
            )

        else:

            raise ValueError(
                f"Unsupported action: {action}"
            )


        state[
            "approval_status"
        ] = "approved"


        state[
            "status"
        ] = "completed"


        state[
            "tool_result"
        ] = result


        db.save_state(
            session_id,
            state
        )


        return {

            "status": "approved",

            "action": action,

            "tool_result":
                result

        }


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
            session_id,
            state
        )


        raise HTTPException(
            status_code=500,
            detail=str(exc)
        )