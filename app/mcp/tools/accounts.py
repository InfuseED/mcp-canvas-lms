"""Account-level Canvas MCP tools."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.canvas.client import CanvasClient
from app.mcp.server import MCPServer, ToolDefinition


def _clean_payload(payload: Optional[Dict[str, Any]], *exclude: str) -> Dict[str, Any]:
    excluded = set(exclude)
    return {k: v for k, v in (payload or {}).items() if k not in excluded and v is not None}


async def _get_account_handler(payload: Optional[Dict[str, Any]], client: CanvasClient) -> Dict[str, Any]:
    if not payload or "account_id" not in payload:
        raise ValueError("'account_id' is required")
    account_id = int(payload["account_id"])
    params = _clean_payload(payload, "account_id")
    account = await client.get_account(account_id, **params)
    return {"account": account}


async def _list_account_courses_handler(payload: Optional[Dict[str, Any]], client: CanvasClient) -> Dict[str, Any]:
    if not payload or "account_id" not in payload:
        raise ValueError("'account_id' is required")
    account_id = int(payload["account_id"])
    params = _clean_payload(payload, "account_id")
    courses = await client.list_account_courses(account_id, **params)
    return {"courses": courses}


async def _list_account_users_handler(payload: Optional[Dict[str, Any]], client: CanvasClient) -> Dict[str, Any]:
    if not payload or "account_id" not in payload:
        raise ValueError("'account_id' is required")
    account_id = int(payload["account_id"])
    params = _clean_payload(payload, "account_id")
    users = await client.list_account_users(account_id, **params)
    return {"users": users}


async def _create_user_handler(payload: Optional[Dict[str, Any]], client: CanvasClient) -> Dict[str, Any]:
    if not payload or "account_id" not in payload:
        raise ValueError("'account_id' is required")
    account_id = int(payload["account_id"])
    user_payload = _clean_payload(payload, "account_id")
    if not user_payload:
        raise ValueError("User payload is required to create a user")
    user = await client.create_user(account_id, user_payload)
    return {"user": user}


async def _list_sub_accounts_handler(payload: Optional[Dict[str, Any]], client: CanvasClient) -> Dict[str, Any]:
    if not payload or "account_id" not in payload:
        raise ValueError("'account_id' is required")
    account_id = int(payload["account_id"])
    params = _clean_payload(payload, "account_id")
    sub_accounts = await client.list_sub_accounts(account_id, **params)
    return {"sub_accounts": sub_accounts}


ACCOUNT_TOOLS: List[ToolDefinition] = [
    ToolDefinition(
        name="canvas_get_account",
        description="Retrieve Canvas account metadata.",
        input_schema={
            "type": "object",
            "properties": {"account_id": {"type": "number", "description": "Canvas account ID."}},
            "required": ["account_id"],
            "additionalProperties": True,
        },
        handler=_get_account_handler,
    ),
    ToolDefinition(
        name="canvas_list_account_courses",
        description="List courses that belong to a Canvas account.",
        input_schema={
            "type": "object",
            "properties": {
                "account_id": {"type": "number"},
                "with_enrollments": {"type": "boolean"},
                "published": {"type": "boolean"},
                "completed": {"type": "boolean"},
                "search_term": {"type": "string"},
                "sort": {"type": "string"},
                "order": {"type": "string"},
            },
            "required": ["account_id"],
            "additionalProperties": True,
        },
        handler=_list_account_courses_handler,
    ),
    ToolDefinition(
        name="canvas_list_account_users",
        description="List users scoped to a Canvas account.",
        input_schema={
            "type": "object",
            "properties": {
                "account_id": {"type": "number"},
                "search_term": {"type": "string"},
                "sort": {"type": "string"},
                "order": {"type": "string"},
            },
            "required": ["account_id"],
            "additionalProperties": True,
        },
        handler=_list_account_users_handler,
    ),
    ToolDefinition(
        name="canvas_create_user",
        description="Create a user (and pseudonym) within a Canvas account.",
        input_schema={
            "type": "object",
            "properties": {
                "account_id": {"type": "number"},
                "user": {
                    "type": "object",
                    "description": "User attributes (name, short_name, time_zone, etc.).",
                    "additionalProperties": True,
                },
                "pseudonym": {
                    "type": "object",
                    "description": "Login credentials for the new user.",
                    "additionalProperties": True,
                },
                "communication_channel": {
                    "type": "object",
                    "description": "Optional channel payload (email/sms).",
                    "additionalProperties": True,
                },
            },
            "required": ["account_id"],
            "additionalProperties": True,
        },
        handler=_create_user_handler,
    ),
    ToolDefinition(
        name="canvas_list_sub_accounts",
        description="List sub-accounts that roll up to a parent account.",
        input_schema={
            "type": "object",
            "properties": {"account_id": {"type": "number"}},
            "required": ["account_id"],
            "additionalProperties": True,
        },
        handler=_list_sub_accounts_handler,
    ),
]


def register_account_tools(server: MCPServer) -> None:
    for tool in ACCOUNT_TOOLS:
        server.register_tool(tool)


__all__ = ["ACCOUNT_TOOLS", "register_account_tools"]
