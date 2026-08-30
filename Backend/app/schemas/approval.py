from pydantic import BaseModel, Field


class ApprovalDecision(BaseModel):
    approved: bool
    comment: str | None = Field(
        default=None,
        max_length=1000
    )