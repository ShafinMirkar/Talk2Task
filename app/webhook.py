import hashlib
import hmac
import json
import time

from fastapi import APIRouter, HTTPException, Request

from app.config import VEXA_WEBHOOK_SECRET

from app.database import (
    get_meeting_by_native_id,
    get_meeting_owner,
    create_action_item,
    update_meeting_status,
)

from app.vexa import get_transcript
from app.transcript import normalize_transcript
from app.processing import process_meeting

from app.jira.users import fetch_project_context


router = APIRouter(
    prefix="/api/webhooks",
    tags=["webhooks"],
)


# ============================================================
# VEXA WEBHOOK SIGNATURE
# ============================================================

def verify_signature(
    body: bytes,
    timestamp: str,
    signature: str,
) -> bool:

    try:
        timestamp_int = int(timestamp)
    except (TypeError, ValueError):
        return False

    # Reject stale/replayed webhooks
    if abs(time.time() - timestamp_int) > 300:
        return False

    message = f"{timestamp}.".encode() + body

    expected = hmac.new(
        VEXA_WEBHOOK_SECRET.encode(),
        message,
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(
        f"sha256={expected}",
        signature,
    )


# ============================================================
# VEXA WEBHOOK
# ============================================================

@router.post("/vexa")
async def handle_webhook(request: Request):

    # --------------------------------------------------------
    # 1. Read raw request
    # --------------------------------------------------------

    body = await request.body()

    timestamp = request.headers.get(
        "X-Webhook-Timestamp"
    )

    signature = request.headers.get(
        "X-Webhook-Signature"
    )

    if not timestamp or not signature:
        raise HTTPException(
            status_code=401,
            detail="Missing webhook signature",
        )

    # --------------------------------------------------------
    # 2. Verify Vexa signature
    # --------------------------------------------------------

    if not verify_signature(
        body,
        timestamp,
        signature,
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid webhook signature",
        )

    # --------------------------------------------------------
    # 3. Parse event
    # --------------------------------------------------------

    data = json.loads(body)

    event_type = data.get("event_type")

    if event_type != "meeting.completed":
        return {
            "status": "ignored"
        }

    meeting_data = data.get(
        "data",
        {},
    ).get(
        "meeting",
        {},
    )

    platform = meeting_data.get(
        "platform"
    )

    native_meeting_id = meeting_data.get(
        "native_meeting_id"
    )

    print(
        f"\nMeeting completed: "
        f"{platform} / {native_meeting_id}"
    )

    # --------------------------------------------------------
    # 4. Find Talk2Task owner
    # --------------------------------------------------------

    clerk_id = get_meeting_owner(
        platform,
        native_meeting_id,
    )

    if not clerk_id:
        print(
            "No Talk2Task owner found for meeting:",
            platform,
            native_meeting_id,
        )

        return {
            "status": "ignored",
            "reason": "meeting_owner_not_found",
        }

    print(
        f"Meeting belongs to Clerk user: {clerk_id}"
    )

    # --------------------------------------------------------
    # 5. Get our MongoDB meeting
    # --------------------------------------------------------

    meeting = get_meeting_by_native_id(
        platform,
        native_meeting_id,
    )

    if not meeting:
        print(
            "Meeting not found in Talk2Task database:",
            platform,
            native_meeting_id,
        )

        return {
            "status": "ignored",
            "reason": "meeting_not_found",
        }

    # --------------------------------------------------------
    # 6. Fetch transcript from Vexa
    # --------------------------------------------------------

    raw_transcript = get_transcript(
        platform,
        native_meeting_id,
    )

    # --------------------------------------------------------
    # 7. Normalize transcript
    # --------------------------------------------------------

    transcript = normalize_transcript(
        raw_transcript
    )

    print(
        "\n========== TRANSCRIPT =========="
    )

    print(
        transcript.to_text()
    )

    print(
        "================================"
    )

    # --------------------------------------------------------
    # 8. Fetch Jira project context
    # --------------------------------------------------------

    jira_context = await fetch_project_context()

    # --------------------------------------------------------
    # 9. Gemini meeting intelligence
    # --------------------------------------------------------

    meeting_date = (
        meeting.get("start_time")
    )

    if not meeting_date:
        meeting_date = (
            time.strftime("%Y-%m-%d")
        )

    intelligence = process_meeting(
        transcript=transcript,
        meeting_date=meeting_date,
        jira_context=jira_context,
    )

    # --------------------------------------------------------
    # 10. Save action items for HITL
    # --------------------------------------------------------

    for item in intelligence.action_items:

        saved_item = create_action_item(
            action_item=item.model_dump(),
            clerk_id=clerk_id,
            meeting_id=meeting["_id"],
        )

        print(
            "\nAction item saved:"
        )

        print(
            f"  Task: {saved_item['task']}"
        )

        print(
            f"  Assignee: "
            f"{saved_item.get('assignee')}"
        )

        print(
            f"  Due: "
            f"{saved_item.get('due_date')}"
        )

        print(
            "  Status: pending_approval"
        )

    # --------------------------------------------------------
    # 11. Mark meeting as processed
    # --------------------------------------------------------

    update_meeting_status(
        platform=platform,
        native_meeting_id=native_meeting_id,
        status="processed",
    )

    # --------------------------------------------------------
    # 12. Print AI result
    # --------------------------------------------------------

    print(
        "\n========== SUMMARY =========="
    )

    print(
        intelligence.summary.summary
    )

    print(
        "\n========== KEY POINTS =========="
    )

    for point in intelligence.summary.key_points:
        print(
            "-",
            point,
        )

    print(
        "\n========== DECISIONS =========="
    )

    for decision in intelligence.decisions:

        print(
            f"- {decision.decision}"
        )

        print(
            f"  Made by: {decision.made_by}"
        )

    print(
        "\n========== ACTION ITEMS =========="
    )

    for item in intelligence.action_items:

        print(
            f"- {item.task}"
        )

        print(
            f"  Assignee: {item.assignee}"
        )

        print(
            f"  Due: {item.due_date}"
        )

    print(
        "================================"
    )

    return {
        "status": "processed",
        "platform": platform,
        "native_meeting_id": native_meeting_id,
        "clerk_id": clerk_id,
        "segments": len(
            transcript.segments
        ),
        "action_items": len(
            intelligence.action_items
        ),
    }