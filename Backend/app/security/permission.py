ROLE_PERMISSIONS = {

    "user": {

        "web_search",

        "calculator",

        "read_document",

        "create_report"

    },

    "admin": {

        "web_search",

        "calculator",

        "read_document",

        "create_report",

        "send_email",

        "publish_report",

        "delete_document"

    }

}


SENSITIVE_ACTIONS = {

    "send_email",

    "publish_report",

    "delete_document"

}


def has_permission(
    role,
    action
):

    return action in (
        ROLE_PERMISSIONS.get(
            role,
            set()
        )
    )


def requires_approval(
    action
):

    if action in SENSITIVE_ACTIONS:

        return True

    safe_actions = {

        "web_search",

        "calculator",

        "read_document",

        "create_report"

    }

    if action not in safe_actions:

        return True

    return False