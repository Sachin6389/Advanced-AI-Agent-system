from typing import Any, TypedDict


class AgentState(TypedDict, total=False):

    # ------------------------------------
    # User / Session
    # ------------------------------------

    user_id: str
    user_role: str
    session_id: str

    # ------------------------------------
    # Request
    # ------------------------------------

    query: str
    recipient: str | None
    action: str | None

    # ------------------------------------
    # Planning
    # ------------------------------------

    plan: list[dict[str, Any]]
    current_step: int

    # ------------------------------------
    # Agent outputs
    # ------------------------------------

    research: str
    file_path: str | None
    analysis: str
    fact_check: str
    report: str

    sources: list[dict[str, Any]]

    # ------------------------------------
    # Memory
    # ------------------------------------

    messages: list[dict[str, str]]
    memories: list[str]
    previous_queries: list[str]

    # ------------------------------------
    # Errors
    # ------------------------------------

    errors: list[str]
    retry_count: int

    # ------------------------------------
    # Workflow
    # ------------------------------------

    status: str
    next_agent: str | None

    # =====================================================
    # Email
    # =====================================================

    email_payload: dict[str, Any] | None

    email_subject: str | None

    email_body: str | None

    # =====================================================
    # Human Approval
    # =====================================================

    approval_required: bool

    approval_status: str | None

    approval_action: str | None

    approval_reason: str | None

    approval: dict[str, Any] | None


    # ------------------------------------
    # Tool execution
    # ------------------------------------
    

    email_sent: bool
    tool_result: Any