import asyncio
import json

import httpx2

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

from app.jira_mcp import (
    MCP_URL,
    get_auth_header,
)

from app.config import ATLASSIAN_CLOUD_ID


async def main():

    headers = {
        "Authorization": get_auth_header(),
    }

    async with httpx2.AsyncClient(
        headers=headers,
        timeout=httpx2.Timeout(30.0, read=300.0),
    ) as http_client:

        async with streamable_http_client(
            MCP_URL,
            http_client=http_client,
        ) as (read_stream, write_stream):

            async with ClientSession(
                read_stream,
                write_stream,
            ) as session:

                await session.initialize()

                print("Connected to Atlassian MCP")

                # --------------------------------------------------
                # 1. Get available transitions
                # --------------------------------------------------

                result = await session.call_tool(
                    "executeRead",
                    {
                        "cloudId": ATLASSIAN_CLOUD_ID,
                        "name": "listJiraIssueTransitions",
                        "inputs": {
                            "issueIdOrKey": "KAN-24",
                        },
                    },
                )

                print("\n========== TRANSITIONS ==========")
                print(result)

                data = json.loads(
                    result.content[0].text
                )

                transitions = data["data"]["transitions"]

                # --------------------------------------------------
                # 2. Find transition whose TARGET is "To Do"
                # --------------------------------------------------

                todo_transition = next(
                    (
                        transition
                        for transition in transitions
                        if transition["to"]["name"].strip().lower()
                        == "to do"
                        and transition.get("isAvailable", False)
                    ),
                    None,
                )

                if not todo_transition:
                    raise RuntimeError(
                        "No available transition to To Do"
                    )

                transition_id = todo_transition["id"]

                print(
                    f"\nFound To Do transition:"
                    f" {todo_transition}"
                )

                print(
                    f"\nUsing transition ID: {transition_id}"
                )

                # --------------------------------------------------
                # 3. Transition the issue
                # --------------------------------------------------

                result = await session.call_tool(
                    "transitionJiraIssue",
                    {
                        "cloudId": ATLASSIAN_CLOUD_ID,
                        "issueIdOrKey": "KAN-24",
                        "transitionId": transition_id,
                    },
                )

                print("\n========== TRANSITION RESULT ==========")
                print(result)
                print("========================================")


if __name__ == "__main__":
    asyncio.run(main())