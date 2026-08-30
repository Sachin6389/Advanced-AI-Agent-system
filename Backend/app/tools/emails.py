from langchain_core.tools import tool


@tool
def send_email(
    recipient: str,
    subject: str,
    body: str
):

    """
    Demo email tool.

    Real email sending should only happen
    after approval.
    """

    return (
        "EMAIL SENT (DEMO)\n"
        f"Recipient: {recipient}\n"
        f"Subject: {subject}\n"
        f"Body length: {len(body)}"
    )


@tool
def publish_report(
    title: str,
    body: str
):

    """
    Demo publishing tool.
    """

    return (
        "REPORT PUBLISHED (DEMO)\n"
        f"Title: {title}\n"
        f"Length: {len(body)}"
    )