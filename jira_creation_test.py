import asyncio

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
import httpx2

from app.config import (
    ATLASSIAN_EMAIL,
    ATLASSIAN_API_TOKEN,
)

from app.jira_mcp import (
    MCP_URL,
    get_auth_header,
    create_jira_issue,
)

from app.models import ActionItem


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

                result = await create_jira_issue(
                    session,
                    ActionItem(
                        task="Test Talk2Task transition",
                        assignee=None,
                        due_date=None,
                    ),
                )

                print("\n========== CREATE RESULT ==========")
                print(result)
                print("====================================")


if __name__ == "__main__":
    asyncio.run(main())