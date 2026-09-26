import os

from fastapi import HTTPException, Request

from clerk_backend_api import (
    AuthenticateRequestOptions,
    authenticate_request,
)


def require_user(request: Request) -> str:
    """
    Verify the Clerk session token and return the Clerk user ID.
    """

    state = authenticate_request(
        request,
        AuthenticateRequestOptions(
            secret_key=os.environ["CLERK_SECRET_KEY"],
            jwt_key=os.environ.get("CLERK_JWT_KEY"),
            authorized_parties=[
                os.environ["FRONTEND_URL"],
            ],
            accepts_token=["session_token"],
        ),
    )

    if not state.is_signed_in:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized",
        )

    return state.payload["sub"]