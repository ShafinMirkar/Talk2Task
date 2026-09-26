from pymongo import MongoClient, ASCENDING
from datetime import datetime, timezone

from app.config import MONGODB_URI, MONGODB_DATABASE


client = MongoClient(MONGODB_URI)

db = client[MONGODB_DATABASE]

users_collection = db["users"]
meetings_collection = db["meetings"]
action_items_collection = db["action_items"]
jira_connections_collection = db["jira_connections"]


# ============================================================
# USERS
# ============================================================

users_collection.create_index(
    [("clerk_id", ASCENDING)],
    unique=True,
)


def save_user(user: dict):
    document = {
        "clerk_id": user["clerk_id"],
        "email": user["email"],
        "first_name": user.get("first_name"),
        "last_name": user.get("last_name"),
        "image_url": user.get("image_url"),
        "created_at": user.get("created_at"),
    }

    users_collection.update_one(
        {"clerk_id": user["clerk_id"]},
        {"$set": document},
        upsert=True,
    )

    return document


def get_user(clerk_id: str):
    return users_collection.find_one(
        {"clerk_id": clerk_id},
        {"_id": 0},
    )


# ============================================================
# MEETINGS
# ============================================================

meetings_collection.create_index(
    [
        ("clerk_id", ASCENDING),
        ("platform", ASCENDING),
        ("native_meeting_id", ASCENDING),
    ],
    unique=True,
)


def save_meeting(
    meeting: dict,
    clerk_id: str | None = None,
):
    existing = meetings_collection.find_one(
        {
            "platform": meeting["platform"],
            "native_meeting_id": meeting["native_meeting_id"],
        }
    )

    owner_id = clerk_id or (
        existing.get("clerk_id")
        if existing
        else None
    )

    document = {
        "platform": meeting["platform"],
        "native_meeting_id": meeting["native_meeting_id"],
        "vexa_meeting_id": meeting.get("id"),
        "meeting_url": meeting.get("constructed_meeting_url"),
        "status": meeting.get("status"),
        "completion_reason": meeting.get("completion_reason"),
        "start_time": meeting.get("start_time"),
        "end_time": meeting.get("end_time"),
        "created_at": meeting.get("created_at"),
        "updated_at": meeting.get("updated_at"),
    }

    if owner_id:
        document["clerk_id"] = owner_id

    meetings_collection.update_one(
        {
            "platform": meeting["platform"],
            "native_meeting_id": meeting["native_meeting_id"],
        },
        {"$set": document},
        upsert=True,
    )

    return document


def get_user_meetings(clerk_id: str):
    return list(
        meetings_collection.find(
            {"clerk_id": clerk_id},
            {"_id": 0},
        ).sort("created_at", -1)
    )


def get_user_meeting(
    clerk_id: str,
    platform: str,
    native_meeting_id: str,
):
    return meetings_collection.find_one(
        {
            "clerk_id": clerk_id,
            "platform": platform,
            "native_meeting_id": native_meeting_id,
        },
        {"_id": 0},
    )


# ============================================================
# ACTION ITEMS
# ============================================================

action_items_collection.create_index(
    [
        ("clerk_id", ASCENDING),
        ("meeting_id", ASCENDING),
    ]
)

action_items_collection.create_index(
    [("status", ASCENDING)]
)


def get_meeting_owner(
    platform: str,
    native_meeting_id: str,
):
    meeting = meetings_collection.find_one(
        {
            "platform": platform,
            "native_meeting_id": native_meeting_id,
        },
        {
            "clerk_id": 1,
        },
    )

    if not meeting:
        return None

    return meeting.get("clerk_id")

def update_meeting_vexa_data(
    platform: str,
    native_meeting_id: str,
    vexa_meeting_id,
    status: str,
):
    meetings_collection.update_one(
        {
            "platform": platform,
            "native_meeting_id": native_meeting_id,
        },
        {
            "$set": {
                "vexa_meeting_id": vexa_meeting_id,
                "status": status,
            }
        },
    )


def get_meeting_by_native_id(
    platform: str,
    native_meeting_id: str,
):
    return meetings_collection.find_one(
        {
            "platform": platform,
            "native_meeting_id": native_meeting_id,
        }
    )


def create_action_item(
    action_item: dict,
    clerk_id: str,
    meeting_id,
):
    document = {
        "clerk_id": clerk_id,
        "meeting_id": meeting_id,

        "task": action_item["task"],
        "assignee": action_item.get("assignee"),
        "due_date": action_item.get("due_date"),

        "status": "pending_approval",

        "jira_issue_key": None,
    }

    result = action_items_collection.insert_one(document)

    document["_id"] = result.inserted_id

    return document

def get_user_action_items(clerk_id: str):
    return list(
        action_items_collection.find(
            {"clerk_id": clerk_id},
            {"_id": 0},
        ).sort("created_at", -1)
    )


def get_meeting_action_items(
    clerk_id: str,
    meeting_id,
):
    return list(
        action_items_collection.find(
            {
                "clerk_id": clerk_id,
                "meeting_id": meeting_id,
            },
            {"_id": 0},
        ).sort("created_at", -1)
    )


def update_action_item(
    clerk_id: str,
    action_item_id,
    updates: dict,
):
    updates["updated_at"] = datetime.now(timezone.utc)

    result = action_items_collection.update_one(
        {
            "_id": action_item_id,
            "clerk_id": clerk_id,
        },
        {
            "$set": updates,
        },
    )

    return result.modified_count > 0


# ============================================================
# JIRA CONNECTIONS
# ============================================================

jira_connections_collection.create_index(
    [("clerk_id", ASCENDING)],
    unique=True,
)


def save_jira_connection(connection: dict):
    document = {
        "clerk_id": connection["clerk_id"],

        "cloud_id": connection["cloud_id"],
        "site_url": connection["site_url"],

        "project_key": connection["project_key"],
        "project_name": connection.get("project_name"),

        "created_at": connection.get("created_at"),
        "updated_at": connection.get("updated_at"),
    }

    jira_connections_collection.update_one(
        {"clerk_id": connection["clerk_id"]},
        {"$set": document},
        upsert=True,
    )

    return document


def get_jira_connection(clerk_id: str):
    return jira_connections_collection.find_one(
        {"clerk_id": clerk_id},
        {"_id": 0},
    )