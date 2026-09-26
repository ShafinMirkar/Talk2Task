from fastapi import FastAPI, Request

from fastapi.middleware.cors import CORSMiddleware

from app.models import Meeting
from app.platforms import validate_meeting
from app.vexa import send_bot
from app.webhook import handle_webhook

from app.auth.routes import router as auth_router
from app.meeting.routes import router as meeting_router
from app.webhook import router as vexa_webhook_router


from fastapi import FastAPI

from app.auth.webhook import router as clerk_webhook_router



app = FastAPI(
    title="Talk2Task",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    clerk_webhook_router,
    prefix="/api",
)
app.include_router(auth_router)
app.include_router(vexa_webhook_router)
app.include_router(meeting_router)

@app.get("/")
def root():
    return {
        "status": "ok",
        "service": "Talk2Task",
    }


@app.post("/meetings/send-bot")
def create_meeting_bot(meeting: Meeting):

    validate_meeting(
        meeting.platform,
        meeting.native_meeting_id,
        meeting.passcode,
    )

    return send_bot(
        platform=meeting.platform.value,
        native_meeting_id=meeting.native_meeting_id,
        passcode=meeting.passcode,
    )

@app.post("/webhooks/vexa")
async def vexa_webhook(
    request: Request,
):
    return await handle_webhook(request)