from typing import Any

from pydantic import (
    BaseModel,
    Field,
)


# ============================================================
# APPROVAL DECISION REQUEST
# ============================================================

class ApprovalDecisionRequest(
    BaseModel
):

    user_id: str = Field(
        min_length=1
    )

    session_id: str = Field(
        min_length=1
    )

    decision: str = Field(
        min_length=1
    )


# ============================================================
# APPROVAL DECISION RESPONSE
# ============================================================

class ApprovalDecisionResponse(
    BaseModel
):

    success: bool

    session_id: str

    status: str

    message: str

    approval: dict[str, Any] | None = None