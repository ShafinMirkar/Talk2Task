from fastapi import APIRouter, Depends, Request

from app.auth.clerk import require_user
from app.database import get_user

router = APIRouter(prefix="/api", tags=["auth"])


@router.get("/me")
def get_current_user(
    request: Request,
    clerk_id: str = Depends(require_user),
):
    user = get_user(clerk_id)

    if not user:
        return {
            "clerk_id": clerk_id,
            "exists": False,
        }

    return {
        "exists": True,
        "user": user,
    }

