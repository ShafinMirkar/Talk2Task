from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.action_items.routes import router as action_items_router
from app.auth.routes import router as auth_router
from app.auth.webhook import router as clerk_webhook_router
from app.meeting.routes import router as meeting_router
from app.webhook import router as vexa_webhook_router


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
app.include_router(action_items_router)


@app.get("/")
def root():
    return {
        "status": "ok",
        "service": "Talk2Task",
    }
