from fastapi import (
    Header,
    HTTPException
)


async def get_current_user(

    x_user_id: str | None = Header(
        default=None
    ),

    x_user_role: str = Header(
        default="user"
    )

):

    if not x_user_id:

        raise HTTPException(
            status_code=401,
            detail=(
                "Missing X-User-Id"
            )
        )

    return {

        "user_id":
            x_user_id,

        "role":
            x_user_role

    }