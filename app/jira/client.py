import base64

import httpx2

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

from app.config import (
    ATLASSIAN_EMAIL,
    ATLASSIAN_API_TOKEN,
)


MCP_URL = "https://mcp.atlassian.com/v2/mcp"


def get_auth_header() -> str:
    credentials = (
        f"{ATLASSIAN_EMAIL}:{ATLASSIAN_API_TOKEN}"
    )

    encoded = base64.b64encode(
        credentials.encode()
    ).decode()

    return f"Basic {encoded}"


def create_http_client():
    return httpx2.AsyncClient(
        headers={
            "Authorization": get_auth_header(),
        },
        timeout=httpx2.Timeout(
            30.0,
            read=300.0,
        ),
    )


def create_mcp_connection(http_client):
    return streamable_http_client(
        MCP_URL,
        http_client=http_client,
    )


def create_mcp_session(
    read_stream,
    write_stream,
):
    return ClientSession(
        read_stream,
        write_stream,
    )