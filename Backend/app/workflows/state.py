from typing import Any, TypedDict


class AgentState(TypedDict, total=False):

    user_id: str

    user_role: str

    session_id: str

    query: str

    recipient: str | None

    # Planning
    plan: list[dict[str, Any]]

    current_step: int

    # Agent outputs
    research: str
    document_content: str

    analysis: str

    fact_check: str

    report: str

    sources: list[dict[str, Any]]

    # Memory
    messages: list[dict[str, str]]

    memories: list[str]

    previous_queries: list[str]

    # Errors
    errors: list[str]

    retry_count: int

    # Workflow
    status: str

    # Human approval
    approval_required: bool

    approval_status: str | None

    approval_action: str | None

    approval_reason: str | None