from langchain_google_genai import ChatGoogleGenerativeAI

from app.config import GOOGLE_API_KEY

from app.models import (
    MeetingIntelligence,
    JiraProjectContext,
)


llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0,
    google_api_key=GOOGLE_API_KEY,
)


structured_llm = llm.with_structured_output(
    MeetingIntelligence
)


SYSTEM_PROMPT = """
You are a meeting intelligence assistant.

Analyze the provided meeting transcript and extract:

1. A concise summary of the meeting.
2. The most important key points discussed.
3. Decisions that were actually made during the meeting.
4. Action items that participants committed to doing.

Rules:

- Do not invent information.
- Only extract decisions explicitly supported by the transcript.
- Only create an action item when someone actually commits to a task.
- Preserve the speaker's name when identifying assignees.
- If an assignee cannot be determined, use null.
- If a due date cannot be determined, use null.
- Convert relative dates such as "tomorrow" or "Friday"
  into an absolute date using the meeting date.
- Keep the summary concise.
- Keep key points focused on meaningful discussion.

Jira assignment rules:

- The available Jira users are provided in the meeting context.
- When an action item has an identifiable assignee,
  match that person to one of the available Jira users.
- Prefer the exact Jira display name when possible.
- Do not invent Jira users.
- If a meeting participant cannot be confidently matched
  to an available Jira user, use null for the assignee.
"""


def analyze_meeting(
    transcript_text: str,
    meeting_date: str,
    jira_context: JiraProjectContext,
) -> MeetingIntelligence:

    jira_users = "\n".join(
        f"- {user.display_name}"
        for user in jira_context.users
        if user.active
    )

    response = structured_llm.invoke(
        [
            (
                "system",
                SYSTEM_PROMPT,
            ),
            (
                "human",
                f"""
Meeting date: {meeting_date}

Available Jira users for project {jira_context.project_key}:

{jira_users}

Analyze this meeting transcript:

--- TRANSCRIPT ---

{transcript_text}

--- END TRANSCRIPT ---
""",
            ),
        ]
    )

    return response