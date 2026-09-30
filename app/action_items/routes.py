import json

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException

from app.auth.clerk import require_user


from app.database import (
    get_action_item,
    get_user_action_items,
    update_action_item,
    update_action_item_status,
    action_items_collection,
)

from app.models import ( ActionItem, ActionItemUpdate, ActionItemReview )

from app.jira.issues import create_jira_issues


router = APIRouter(
    prefix="/api/action-items",
    tags=["action-items"],
)


# ============================================================
# GET ALL ACTION ITEMS
# ============================================================

@router.get("")
def list_action_items(
    clerk_id: str = Depends(require_user),
):
    return {
        "action_items": get_user_action_items(clerk_id)
    }


# ============================================================
# GET ONE ACTION ITEM
# ============================================================

@router.get("/{action_item_id}")
def get_one_action_item(
    action_item_id: str,
    clerk_id: str = Depends(require_user),
):
    try:
        object_id = ObjectId(action_item_id)

    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Invalid action item ID",
        )

    item = get_action_item(
        clerk_id,
        object_id,
    )

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Action item not found",
        )

    item["_id"] = str(item["_id"])

    if isinstance(item.get("meeting_id"), ObjectId):
        item["meeting_id"] = str(item["meeting_id"])

    return item


# ============================================================
# EDIT ACTION ITEM
# ============================================================

@router.patch("/{action_item_id}")
def edit_action_item(
    action_item_id: str,
    payload: ActionItemUpdate,
    clerk_id: str = Depends(require_user),
):
    try:
        object_id = ObjectId(action_item_id)

    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Invalid action item ID",
        )

    updates = payload.model_dump(
        exclude_none=True
    )

    if not updates:
        raise HTTPException(
            status_code=400,
            detail="No fields to update",
        )

    allowed_fields = {
        "task",
        "assignee",
        "due_date",
    }

    updates = {
        key: value
        for key, value in updates.items()
        if key in allowed_fields
    }

    updated = update_action_item(
        clerk_id=clerk_id,
        action_item_id=object_id,
        updates=updates,
    )

    if not updated:
        raise HTTPException(
            status_code=404,
            detail="Action item not found or already processed",
        )

    updated["_id"] = str(updated["_id"])

    if isinstance(updated.get("meeting_id"), ObjectId):
        updated["meeting_id"] = str(
            updated["meeting_id"]
        )

    return updated


@router.post("/review")
async def review_action_items(
    review: ActionItemReview,
    clerk_id: str = Depends(require_user),
):
    print("\n========== ACTION ITEM REVIEW ==========")
    print(f"[REVIEW] Approved: {len(review.approved)}")
    print(f"[REVIEW] Rejected: {len(review.rejected)}")
    
    approved_ids = review.approved
    rejected_ids = review.rejected

    all_ids = approved_ids + rejected_ids

    if not all_ids:
        raise HTTPException(
            status_code=400,
            detail="No action items were reviewed",
        )

    # Prevent duplicate IDs
    if len(all_ids) != len(set(all_ids)):
        raise HTTPException(
            status_code=400,
            detail="Duplicate action item IDs",
        )

    action_items = []

    for item_id in all_ids:

        if not ObjectId.is_valid(item_id):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid action item ID: {item_id}",
            )

        item = action_items_collection.find_one({
            "_id": ObjectId(item_id),
            "clerk_id": clerk_id,
        })

        if not item:
            raise HTTPException(
                status_code=404,
                detail=f"Action item not found: {item_id}",
            )

        if item.get("status") is not None:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Action item {item_id} "
                    f"has already been reviewed"
                ),
            )

        action_items.append(item)

    approved_items = [
        item
        for item in action_items
        if str(item["_id"]) in approved_ids
    ]

    rejected_items = [
        item
        for item in action_items
        if str(item["_id"]) in rejected_ids
    ]

    # Reject items first
    for item in rejected_items:
        update_action_item_status(
            str(item["_id"]),
            clerk_id,
            "rejected",
        )

    # Convert approved MongoDB documents
    jira_action_items = [
        ActionItem(
            task=item["task"],
            assignee=item.get("assignee"),
            due_date=item.get("due_date"),
        )
        for item in approved_items
    ]

    jira_results = []

    if jira_action_items:
        jira_results = await create_jira_issues(
            jira_action_items
        )

    # Match Jira results back to MongoDB action items
    for item, jira_result in zip(
        approved_items,
        jira_results,
    ):
        update_action_item_status(
            str(item["_id"]),
            clerk_id,
            "jira_created",
            jira_issue_key=jira_result["issue_key"],
        )

    return {
        "message": "Action items reviewed",
        "approved": len(approved_items),
        "rejected": len(rejected_items),
        "jira_created": jira_results,
    }