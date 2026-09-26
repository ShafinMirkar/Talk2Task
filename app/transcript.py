from app.models import (
    MeetingTranscript,
    TranscriptSegment,
)


def normalize_transcript(
    data: dict,
) -> MeetingTranscript:

    segments = []

    for segment in data.get("segments", []):

        if not segment.get("completed", False):
            continue

        text = segment.get("text", "").strip()

        if not text:
            continue

        segments.append(
            TranscriptSegment(
                speaker=segment.get("speaker"),
                text=text,
                start=segment.get("start", 0),
                end=segment.get("end", 0),
                language=segment.get("language"),
            )
        )

    return MeetingTranscript(
        meeting_id=str(data["id"]),
        platform=data["platform"],
        native_meeting_id=data["native_meeting_id"],
        segments=segments,
    )