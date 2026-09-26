import json

from mcp import ClientSession

from app.config import (
    ATLASSIAN_CLOUD_ID,
    JIRA_PROJECT_KEY,
)

from app.models import (
    JiraProjectContext,
    JiraUser,
)


async def get_assignable_users(
    session: ClientSession,
):
    result = await session.call_tool(
        "executeRead",
        {
            "cloudId": ATLASSIAN_CLOUD_ID,
            "name": "listJiraIssueAssignableUsers",
            "inputs": {
                "project": JIRA_PROJECT_KEY,
            },
        },
    )

    data = json.loads(
        result.content[0].text
    )

    return data["data"]


async def fetch_jira_project_context(
    session: ClientSession,
) -> JiraProjectContext:

    users = await get_assignable_users(
        session
    )

    jira_users = [
        JiraUser(
            account_id=user["accountId"],
            display_name=user["displayName"],
            active=user.get(
                "active",
                True,
            ),
        )
        for user in users
    ]

    return JiraProjectContext(
        project_key=JIRA_PROJECT_KEY,
        users=jira_users,
    )


async def fetch_project_context():
    from app.jira.client import (
        create_http_client,
        create_mcp_connection,
        create_mcp_session,
    )

    async with create_http_client() as http_client:

        async with create_mcp_connection(
            http_client
        ) as (
            read_stream,
            write_stream,
        ):

            async with create_mcp_session(
                read_stream,
                write_stream,
            ) as session:

                await session.initialize()

                return await fetch_jira_project_context(
                    session
                )


async def resolve_jira_user(
    session: ClientSession,
    name: str | None,
):
    if not name:
        return None

    users = await get_assignable_users(
        session
    )

    name_lower = name.strip().lower()

    for user in users:

        display_name = (
            user.get(
                "displayName",
                "",
            )
            .strip()
            .lower()
        )

        if display_name == name_lower:
            return user["accountId"]

    return None