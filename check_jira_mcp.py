"""
Run from the project root:   python scripts/check_jira_mcp.py

Sends a raw MCP `initialize` request to each candidate Atlassian endpoint
using your configured credentials and prints the HTTP status and reply body,
so you can see WHY the server rejects the handshake. Secrets are never printed.
"""
import base64
import json

import httpx

from app.config import ATLASSIAN_EMAIL, ATLASSIAN_API_TOKEN

ENDPOINTS = [
    "https://mcp.atlassian.com/v2/mcp",   # what the app uses today
    "https://mcp.atlassian.com/v1/mcp",   # endpoint shown in Atlassian's API-token docs
]

auth = base64.b64encode(f"{ATLASSIAN_EMAIL}:{ATLASSIAN_API_TOKEN}".encode()).decode()

payload = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
        "protocolVersion": "2025-03-26",
        "capabilities": {},
        "clientInfo": {"name": "talk2task-check", "version": "0"},
    },
}

for url in ENDPOINTS:
    print(f"\n=== {url}")
    try:
        r = httpx.post(
            url,
            json=payload,
            headers={
                "Authorization": f"Basic {auth}",
                "Accept": "application/json, text/event-stream",
            },
            timeout=30,
        )
        print("HTTP", r.status_code)
        print(r.text[:800])
    except Exception as e:
        print("request failed:", repr(e))
