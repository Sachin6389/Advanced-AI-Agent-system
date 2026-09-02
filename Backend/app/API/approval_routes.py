
import logging

from fastapi import (
    APIRouter,
    HTTPException,
    Depends,
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
from app.security.auth import(get_current_user)

from app.schemas.approval import (
    ApprovalDecisionRequest,
    ApprovalDecisionResponse,
)

from app.workflows.email_workflow import (
    execute_approved_email,
)


# =========================================================
# Logger
# =========================================================

logger = logging.getLogger(
    __name__
)


# =========================================================
# Router
# =========================================================

router = APIRouter(
    prefix="/approval",
    tags=["Approval"],
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
# Decide Approval
# =========================================================

@router.post(
        "",
    response_model=ApprovalDecisionResponse
)
async def decide_approval(
    request: ApprovalDecisionRequest,
    current_user=Depends(
        get_current_user
    )
):

    # =====================================================
    # 1. Validate decision
    # =====================================================

    decision = request.decision.strip().lower()

    if decision not in {
        "accept",
        "approve",
        "reject",
        "rejected",
    }:
        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid decision. "
                "Use 'accept' or 'reject'."
            ),
        )

    # Normalize decision
    approved = decision in {
        "accept",
        "approve",
    }

    state = db.load_state(
        request.session_id
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

    # =====================================================
    # 2. Get approval from DB
    # =====================================================

    approval = approval_manager.get(
        request.session_id
    )

    if not approval:
        raise HTTPException(
            status_code=404,
            detail="Approval not found.",
        )


    # =====================================================
    # 5. Verify pending status
    # =====================================================

    if approval.get("status") != "pending":

        return ApprovalDecisionResponse(
            success=False,
            session_id=request.session_id,
            status=approval.get(
                "status",
                "unknown",
            ),
            message=(
                "This approval has already "
                "been processed."
            ),
            approval=approval,
        )

    # =====================================================
    # 6. Save user decision
    # =====================================================

    try:

        updated_approval = (
            approval_manager.decide(
                session_id=request.session_id,
                approved=approved,
                comment=None,
            )
        )

    except Exception as exc:

        logger.exception(
            "Failed to save approval decision: %s",
            exc,
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to save approval decision.",
        )

    # =====================================================
    # 7. REJECT
    # =====================================================

    if not approved:

        logger.info(
            "Email approval rejected: session=%s",
            request.session_id,
        )

        return ApprovalDecisionResponse(
            success=True,
            session_id=request.session_id,
            status="rejected",
            message=(
                " ❌ Email was rejected. "
                "The email was not sent."
            ),
            approval=updated_approval,
        )

    # =====================================================
    # 8. ACCEPT
    # =====================================================

    try:

        email_result = (
            await execute_approved_email(
                session_id=request.session_id,
            )
        )

    except PermissionError as exc:

        logger.warning(
            "Email execution blocked: %s",
            exc,
        )

        raise HTTPException(
            status_code=403,
            detail=str(exc),
        )

    except ValueError as exc:

        logger.warning(
            "Invalid approved email: %s",
            exc,
        )

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except Exception as exc:

        logger.exception(
            "Approved email execution failed: %s",
            exc,
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to execute approved email.",
        )

    # =====================================================
    # 9. Email successfully sent
    # =====================================================

    return ApprovalDecisionResponse(
        success=True,
        session_id=request.session_id,
        status="email_sent",
        message=(
            " ✅ Email approval accepted and "
            "email was sent successfully."
        ),
        approval=updated_approval,
    )

