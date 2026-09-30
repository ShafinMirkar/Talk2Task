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
    """
    Review action items in one batch.

    Safe to retry: nothing is marked until it has actually happened.
    - Approved items are marked `jira_created` one by one, right after
      Jira creates them.
    - Rejected items are marked only after every approved item succeeded.
    - On a retry, items that are already in the requested final state
      are skipped instead of causing an error or a duplicate Jira issue.
    """
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

    def load(item_id: str) -> dict:
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

        return item

    def result_for(item: dict) -> dict:
        return {
            "issue_key": item.get("jira_issue_key"),
            "task": item["task"],
            "assignee": item.get("assignee"),
        }

    pending_approved = []   # still to be sent to Jira
    done_results = []       # already created in Jira (earlier attempt)
    pending_rejected = []   # still to be marked rejected

    for item_id in approved_ids:
        item = load(item_id)
        status = item.get("status")

        if status is None:
            pending_approved.append(item)
        elif status == "jira_created":
            done_results.append(result_for(item))
        else:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Action item {item_id} "
                    f"has already been reviewed"
                ),
            )

    for item_id in rejected_ids:
        item = load(item_id)
        status = item.get("status")

        if status is None:
            pending_rejected.append(item)
        elif status != "rejected":
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Action item {item_id} "
                    f"has already been reviewed"
                ),
            )

    # ---- 1. Jira first. Each item is saved the moment it is created.
    new_results = []

    if pending_approved:
        jira_action_items = [
            ActionItem(
                task=item["task"],
                assignee=item.get("assignee"),
                due_date=item.get("due_date"),
            )
            for item in pending_approved
        ]

        def on_created(index: int, result: dict):
            update_action_item_status(
                str(pending_approved[index]["_id"]),
                clerk_id,
                "jira_created",
                jira_issue_key=result["issue_key"],
            )

        try:
            new_results = await create_jira_issues(
                jira_action_items,
                on_created=on_created,
            )
        except Exception as error:
            print(f"[REVIEW] Jira creation failed: {error!r}")

            # Nothing else has been marked, and issues created so far
            # are already saved, so the client can safely retry.
            raise HTTPException(
                status_code=502,
                detail="Could not create Jira tasks",
            )

    # ---- 2. Only now mark rejections.
    for item in pending_rejected:
        update_action_item_status(
            str(item["_id"]),
            clerk_id,
            "rejected",
        )

    return {
        "message": "Action items reviewed",
        "approved": len(approved_ids),
        "rejected": len(rejected_ids),
        "jira_created": done_results + new_results,
    }
