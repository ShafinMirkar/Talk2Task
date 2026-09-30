from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class Platform(str, Enum):
    GOOGLE_MEET = "google_meet"
    TEAMS = "teams"


class Meeting(BaseModel):
    platform: Platform
    native_meeting_id: str
    passcode: str | None = None


class TranscriptSegment(BaseModel):
    speaker: str | None = None
    text: str
    start: float = 0
    end: float = 0
    language: str | None = None


class MeetingTranscript(BaseModel):
    meeting_id: str
    platform: Platform
    native_meeting_id: str
    segments: list[TranscriptSegment]

    def to_text(self) -> str:
        return "\n".join(
            f"{segment.speaker or 'Unknown'}: {segment.text}"
            for segment in self.segments
        )


# -------------------------
# Phase 3: LLM output
# -------------------------

class MeetingSummary(BaseModel):
    summary: str
    key_points: list[str]


class Decision(BaseModel):
    decision: str
    made_by: str | None = None


class ActionItem(BaseModel):
    task: str
    assignee: str | None = None
    due_date: str | None = None

class ActionItemUpdate(BaseModel):
    task: str | None = None
    assignee: str | None = None
    due_date: str | None = None

class MeetingIntelligence(BaseModel):
    summary: MeetingSummary
    decisions: list[Decision]
    action_items: list[ActionItem]

class JiraUser(BaseModel):
    account_id: str
    display_name: str
    active: bool = True


class JiraProjectContext(BaseModel):
    project_key: str
    users: list[JiraUser]

class User(BaseModel):
    clerk_id: str
    email: str
    first_name: str | None = None
    last_name: str | None = None
    image_url: str | None = None
    created_at: datetime

class ActionItemReview(BaseModel):
    approved: list[str] = []
    rejected: list[str] = []