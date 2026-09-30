from app.models import Platform


def validate_meeting(
    platform: Platform,
    meeting_id: str,
    passcode: str | None = None,
):
    if platform == Platform.GOOGLE_MEET:
        if passcode:
            raise ValueError(
                "Google Meet does not require a passcode"
            )

    elif platform == Platform.TEAMS:
        if not meeting_id:
            raise ValueError(
                "Teams meeting ID is required"
            )

    return True