import json

from mcp import ClientSession

from app.config import (
    ATLASSIAN_CLOUD_ID,
    JIRA_PROJECT_KEY,
)

from app.models import ActionItem

from app.jira.users import resolve_jira_user
from app.jira.transitions import (
    transition_issue_to_todo,
)


async def create_jira_issue(
    session: ClientSession,
    action_item: ActionItem,
):

    account_id = await resolve_jira_user(
        session,
        action_item.assignee,
    )

    description = (
        "Created from Talk2Task meeting "
        "action item.\n\n"
        f"Task: {action_item.task}\n"
        f"Assignee: "
        f"{action_item.assignee or 'Unassigned'}\n"
        f"Due date: "
        f"{action_item.due_date or 'No due date'}"
    )

    payload = {
        "cloudId": ATLASSIAN_CLOUD_ID,
        "projectKey": JIRA_PROJECT_KEY,
        "summary": action_item.task,
        "issueType": "Task",
        "description": description,
    }

    if account_id:
        payload["assignee"] = account_id

    return await session.call_tool(
        "createJiraIssue",
        payload,
    )

async def create_jira_issues(
    action_items: list[ActionItem],
    on_created=None,
):
    """
    Create one Jira issue per action item.

    on_created(index, result) is called synchronously as soon as each
    issue exists in Jira, so the caller can persist it immediately.
    If a later item fails, earlier issues are already recorded and a
    retry will not create duplicates.
    """
    from app.jira.client import (
        create_http_client,
        create_mcp_connection,
        create_mcp_session,
    )

    async with create_http_client() as http_client:
        async with create_mcp_connection(
            http_client
        ) as (read_stream, write_stream):

            async with create_mcp_session(
                read_stream,
                write_stream,
            ) as session:

                print("[JIRA MCP] Session initialized")
                await session.initialize()

                results = []

                for item in action_items:
                    print(
                        f"[JIRA MCP] Creating issue: {item.task}"
                    )
                    print(
                        f"[JIRA MCP] Assignee: "
                        f"{item.assignee or 'Unassigned'}"
                    )
                    result = await create_jira_issue(
                        session,
                        item,
                    )

                    created_data = json.loads(
                        result.content[0].text
                    )

                    issue_key = (
                        created_data["data"]["key"]
                    )

                    print(
                        f"[JIRA MCP] Created: {issue_key}"
                    )

                    result_item = {
                        "issue_key": issue_key,
                        "task": item.task,
                        "assignee": item.assignee,
                    }

                    # Persist right away: the issue exists now.
                    if on_created:
                        on_created(len(results), result_item)

                    results.append(result_item)

                    # A failed transition must not fail the item
                    # (the issue already exists; retrying would duplicate it).
                    try:
                        await transition_issue_to_todo(
                            session,
                            issue_key,
                        )

                        print(
                            f"[JIRA MCP] {issue_key} -> To Do"
                        )
                    except Exception as error:
                        print(
                            f"[JIRA MCP] Could not transition "
                            f"{issue_key}: {error}"
                        )
                    
                print(
                    f"[JIRA MCP] Finished. "
                    f"Created {len(results)} issues."
                )
                return results