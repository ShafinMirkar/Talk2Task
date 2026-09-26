import requests
import httpx

from app.config import (
    VEXA_API_BASE,
    VEXA_BOT_API_KEY,
    VEXA_TX_API_KEY,
)


def _headers(api_key: str):
    return {
        "X-API-Key": api_key,
        "Content-Type": "application/json",
    }


async def start_meeting_bot(
    platform: str,
    meeting_url: str,
    passcode: str | None = None,
):
    """
    Start a Vexa bot using the full meeting URL.

    Used when a user creates a meeting through Talk2Task.
    Vexa parses the native meeting ID from the URL.
    """

    payload = {
        "platform": platform,
        "meeting_url": meeting_url,
        "bot_name": "Talk2Task",
        "transcribe_enabled": True,
        "recording_enabled": True,
    }

    if passcode:
        payload["passcode"] = passcode

    headers = {
        "X-API-Key": VEXA_BOT_API_KEY,
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{VEXA_API_BASE}/bots",
            json=payload,
            headers=headers,
            timeout=30,
        )

        response.raise_for_status()

        return response.json()


def send_bot(
    platform: str,
    native_meeting_id: str,
    passcode: str | None = None,
):
    """
    Start a Vexa bot using a native meeting ID.

    Kept for the existing/native-ID workflow.
    """

    payload = {
        "platform": platform,
        "native_meeting_id": native_meeting_id,
        "bot_name": "Talk2Task",
        "transcribe_enabled": True,
        "recording_enabled": True,
    }

    if passcode:
        payload["passcode"] = passcode

    response = requests.post(
        f"{VEXA_API_BASE}/bots",
        headers=_headers(VEXA_BOT_API_KEY),
        json=payload,
        timeout=30,
    )

    response.raise_for_status()

    return response.json()


def get_transcript(
    platform: str,
    native_meeting_id: str,
):
    """
    Fetch the completed transcript from Vexa.
    """

    response = requests.get(
        f"{VEXA_API_BASE}/transcripts/"
        f"{platform}/{native_meeting_id}",
        headers=_headers(VEXA_TX_API_KEY),
        timeout=30,
    )

    response.raise_for_status()

    return response.json()