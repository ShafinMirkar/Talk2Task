import os
import json

from fastapi import APIRouter, HTTPException, Request
from svix.webhooks import Webhook
from app.database import save_user


router = APIRouter(
    prefix="/webhooks",
    tags=["webhooks"],
)


@router.post("/clerk")
async def clerk_webhook(
    request: Request,
):
    # Get raw request body.
    body = await request.body()

    # Get Clerk/Svix signature headers.
    svix_id = request.headers.get(
        "svix-id"
    )
    svix_timestamp = request.headers.get(
        "svix-timestamp"
    )
    svix_signature = request.headers.get(
        "svix-signature"
    )

    if not all(
        [
            svix_id,
            svix_timestamp,
            svix_signature,
        ]
    ):
        raise HTTPException(
            status_code=400,
            detail="Missing webhook headers",
        )

    signing_secret = os.environ.get(
        "CLERK_WEBHOOK_SIGNING_SECRET"
    )

    if not signing_secret:
        raise HTTPException(
            status_code=500,
            detail="Clerk webhook signing secret not configured",
        )

    try:
        webhook = Webhook(
            signing_secret
        )
        print("Clerk webhook headers:")
        print("svix-id:", svix_id)
        print("svix-timestamp:", svix_timestamp)
        print("svix-signature:", svix_signature)
        print("body length:", len(body))
        event = webhook.verify(
            body,
            {
                "svix-id": svix_id,
                "svix-timestamp": svix_timestamp,
                "svix-signature": svix_signature,
            },
        )

        event = json.loads(body)

        event_type = event.get("type")
        data = event.get("data", {})

    except Exception as e:
        print(
            "CLERK WEBHOOK VERIFICATION ERROR:",
            repr(e),
        )

        raise HTTPException(
            status_code=400,    
            detail="Invalid webhook signature",
        )

    event_type = event.get("type")
    data = event.get("data", {})

    print(
        f"Clerk webhook received: "
        f"{event_type}"
    )

    if event_type == "user.created":

        clerk_id = data.get("id")

        email_addresses = data.get(
            "email_addresses",
            [],
        )

        primary_email_id = data.get(
            "primary_email_address_id"
        )

        email = None

        for address in email_addresses:
            if (
                address.get("id")
                == primary_email_id
            ):
                email = address.get(
                    "email_address"
                )
                break

        user = {
            "clerk_id": clerk_id,
            "email": email,
            "first_name": data.get("first_name"),
            "last_name": data.get("last_name"),
            "image_url": data.get("image_url"),
            "created_at": data.get("created_at"),
        }

        saved_user = save_user(user)

        print(
            "User saved to MongoDB:",
            saved_user,
        )

        # MongoDB insertion will go here.

    return {
        "success": True
    }