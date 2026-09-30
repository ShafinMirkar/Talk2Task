from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from pydantic import BaseModel

from app.auth.clerk import require_user

from app.database import (
    get_meeting_by_native_id,
    get_meeting_by_id,
    save_meeting,
    update_meeting_vexa_data,
)
from app.models import Platform
from app.vexa import start_meeting_bot
from app.vexa import get_meeting_status

router = APIRouter(
    prefix="/api/meetings",
    tags=["meetings"],
)


class CreateMeetingRequest(BaseModel):
    meeting_url: str
    passcode: str | None = None

def detect_platform(meeting_url: str) -> Platform:
    url = meeting_url.lower()

    if "meet.google.com" in url:
        return Platform.GOOGLE_MEET

    if (
        "teams.live.com" in url
        or "teams.microsoft.com" in url
    ):
        return Platform.TEAMS

    raise HTTPException(
        status_code=400,
        detail="Unsupported meeting URL",
    )

@router.post("")
async def create_meeting(
    request: CreateMeetingRequest,
    clerk_id: str = Depends(require_user),
):
    # 1. Detect platform
    platform = detect_platform(request.meeting_url)

    # 2. Start Vexa
    vexa_meeting = await start_meeting_bot(
        platform=platform.value,
        meeting_url=request.meeting_url,
        passcode=request.passcode,
    )

    # Vexa parses the native meeting ID from the URL
    native_meeting_id = vexa_meeting.get(
        "native_meeting_id"
    )

    # 3. Save meeting ownership
    meeting = {
        "platform": platform.value,
        "native_meeting_id": native_meeting_id,
        "meeting_url": request.meeting_url,
        "status": vexa_meeting.get(
            "status",
            "requested",
        ),
    }

    save_meeting(
        meeting=meeting,
        clerk_id=clerk_id,
    )

    # 4. Save Vexa information
    update_meeting_vexa_data(
        platform=platform.value,
        native_meeting_id=native_meeting_id,
        vexa_meeting_id=vexa_meeting.get("id"),
        status=vexa_meeting.get(
            "status",
            "requested",
        ),
    )

    # 5. Return meeting
    saved_meeting = get_meeting_by_native_id(
    platform.value,
    native_meeting_id,
    )
    
    if saved_meeting and "_id" in saved_meeting:
        saved_meeting["_id"] = str(saved_meeting["_id"])
    
    return {
        "meeting": saved_meeting,
    }

# Statuses set by Talk2Task itself (webhook), not by Vexa.
# Vexa only knows about the meeting lifecycle (…/completed);
# post-meeting AI processing is tracked in MongoDB.
LOCAL_STATUSES = {"analyzing", "processed"}


@router.get("/{meeting_id}/status")
async def meeting_status(
    meeting_id: str,
    clerk_id: str = Depends(require_user),
):
    meeting = get_meeting_by_id(
        meeting_id,
        clerk_id,
    )

    if not meeting:
        raise HTTPException(
            status_code=404,
            detail="Meeting not found",
        )

    # Once the webhook has taken over, MongoDB is the source of truth.
    if meeting.get("status") in LOCAL_STATUSES:
        return {
            "meeting_id": meeting_id,
            "status": meeting["status"],
            "completion_reason": meeting.get("completion_reason"),
            "start_time": meeting.get("start_time"),
            "end_time": meeting.get("end_time"),
        }

    # Otherwise report Vexa's live lifecycle status.
    status = await get_meeting_status(
        vexa_meeting_id=meeting["vexa_meeting_id"],
    )

    print(
        f"[MEETING STATUS] "
        f"{meeting_id} -> {status['status']}"
    )

    return {
        "meeting_id": meeting_id,
        **status,
    }
