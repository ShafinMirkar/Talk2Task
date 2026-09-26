import os
from dotenv import load_dotenv

load_dotenv()

VEXA_API_BASE = os.getenv(
    "VEXA_API_BASE",
    "https://api.cloud.vexa.ai",
)

VEXA_BOT_API_KEY = os.getenv("VEXA_BOT_API_KEY")
VEXA_TX_API_KEY = os.getenv("VEXA_TX_API_KEY")
VEXA_WEBHOOK_SECRET = os.getenv("VEXA_WEBHOOK_SECRET")

MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DATABASE = os.getenv(
    "MONGODB_DATABASE",
    "talk2task",
)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

ATLASSIAN_EMAIL = os.getenv("ATLASSIAN_EMAIL")
ATLASSIAN_API_TOKEN = os.getenv("ATLASSIAN_API_TOKEN")

ATLASSIAN_CLOUD_ID = os.getenv("ATLASSIAN_CLOUD_ID")
JIRA_PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY")