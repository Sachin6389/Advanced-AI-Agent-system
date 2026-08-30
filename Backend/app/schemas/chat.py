from typing import Any

from pydantic import (
    BaseModel,
    Field
)


class ChatRequest(BaseModel):

    user_id: str = Field(
        min_length=1
    )

    session_id: str = Field(
        min_length=1
    )

    message: str = Field(
        min_length=1
    )

    recipient: str | None = None


class ChatResponse(BaseModel):

    session_id: str

    status: str

    answer: str | None = None

    plan: list[
        dict[str, Any]
    ] = []

    sources: list[
        dict[str, Any]
    ] = []

    approval_required: bool = False

    approval: dict[str, Any] | None = None

    errors: list[str] = []