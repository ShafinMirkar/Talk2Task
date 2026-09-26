# from datetime import date

# from app.intelligence import analyze_meeting

# from app.models import MeetingTranscript, JiraProjectContext


# def process_meeting(
#     transcript: MeetingTranscript,
#     meeting_date,
#     jira_context: JiraProjectContext,
# ):
#     return analyze_meeting(
#         transcript_text=transcript.to_text(),
#         meeting_date=meeting_date,
#         jira_context=jira_context,
#     )
from app.intelligence import analyze_meeting
from app.models import (
    MeetingTranscript,
    JiraProjectContext,
)


def process_meeting(
    transcript: MeetingTranscript,
    meeting_date,
    jira_context: JiraProjectContext,
):
    return analyze_meeting(
        transcript_text=transcript.to_text(),
        meeting_date=meeting_date,
        jira_context=jira_context,
    )