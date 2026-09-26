import json

from mcp import ClientSession

from app.config import ATLASSIAN_CLOUD_ID


async def get_issue_transitions(
    session: ClientSession,
    issue_key: str,
):
    result = await session.call_tool(
        "executeRead",
        {
            "cloudId": ATLASSIAN_CLOUD_ID,
            "name": "listJiraIssueTransitions",
            "inputs": {
                "issueIdOrKey": issue_key,
            },
        },
    )

    data = json.loads(
        result.content[0].text
    )

    return data["data"]["transitions"]


async def find_transition_to_status(
    session: ClientSession,
    issue_key: str,
    target_status: str,
):
    transitions = await get_issue_transitions(
        session,
        issue_key,
    )

    target_status_lower = (
        target_status.strip().lower()
    )

    for transition in transitions:

        target = transition.get(
            "to",
            {},
        )

        target_name = (
            target.get(
                "name",
                "",
            )
            .strip()
            .lower()
        )

        if (
            target_name == target_status_lower
            and transition.get(
                "isAvailable",
                False,
            )
        ):
            return transition

    return None


async def transition_issue(
    session: ClientSession,
    issue_key: str,
    target_status: str,
):
    transition = await find_transition_to_status(
        session,
        issue_key,
        target_status,
    )

    if not transition:
        raise RuntimeError(
            f"No available transition to "
            f"'{target_status}' for {issue_key}"
        )

    transition_id = transition["id"]

    print(
        f"Transitioning {issue_key} "
        f"to {target_status} "
        f"using transition {transition_id}"
    )

    return await session.call_tool(
        "transitionJiraIssue",
        {
            "cloudId": ATLASSIAN_CLOUD_ID,
            "issueIdOrKey": issue_key,
            "transitionId": transition_id,
        },
    )


async def transition_issue_to_todo(
    session: ClientSession,
    issue_key: str,
):
    return await transition_issue(
        session,
        issue_key,
        "To Do",
    )