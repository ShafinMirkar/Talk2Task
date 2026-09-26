from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.auth.clerk import require_user
from app.database import (
    get_meeting_by_native_id,
    save_meeting,
    update_meeting_vexa_data,
)
from app.models import Platform
from app.vexa import start_meeting_bot


router = APIRouter(
    prefix="/api/meetings",
    tags=["meetings"],
)


class CreateMeetingRequest(BaseModel):
    platform: Platform
    native_meeting_id: str
    meeting_url: str
    passcode: str | None = None


@router.post("")
async def create_meeting(
    request: CreateMeetingRequest,
    clerk_id: str = Depends(require_user),
):
    # --------------------------------------------------
    # 1. Save the meeting first
    #
    # This is important because the Vexa webhook does
    # not contain the Clerk user ID.
    # --------------------------------------------------

    meeting = {
        "platform": request.platform.value,
        "native_meeting_id": request.native_meeting_id,
        "meeting_url": request.meeting_url,
        "status": "requested",
    }

    save_meeting(
        meeting=meeting,
        clerk_id=clerk_id,
    )

    # --------------------------------------------------
    # 2. Start Vexa bot
    # --------------------------------------------------

    vexa_meeting = await start_meeting_bot(
        platform=request.platform.value,
        meeting_url=request.meeting_url,
        passcode=request.passcode,
    )

    # --------------------------------------------------
    # 3. Store Vexa information
    # --------------------------------------------------

    update_meeting_vexa_data(
        platform=request.platform.value,
        native_meeting_id=request.native_meeting_id,
        vexa_meeting_id=vexa_meeting.get("id"),
        status=vexa_meeting.get("status", "requested"),
    )

    # --------------------------------------------------
    # 4. Return the meeting
    # --------------------------------------------------

    saved_meeting = get_meeting_by_native_id(
        request.platform.value,
        request.native_meeting_id,
    )

    return {
        "meeting": saved_meeting,
    }