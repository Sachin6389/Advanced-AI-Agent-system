import logging


logger = logging.getLogger(
    __name__
)


async def send_email_tool(
    recipient: str,
    subject: str,
    body: str,
):
    """
    Actually sends the email.

    This function must ONLY be called
    after human approval.
    """

    logger.info(
        "Sending email to %s",
        recipient,
    )

    # -----------------------------------------------------
    # Put your actual email provider here.
    #
    # Example:
    #
    # SMTP
    # Gmail API
    # Outlook API
    # Resend
    # SendGrid
    # etc.
    # -----------------------------------------------------

    # result = await email_provider.send(...)

    result = {
        "success": True,
        "recipient": recipient,
        "subject": subject,
        "body": body,
    }

    return result