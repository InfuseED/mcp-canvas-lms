"""User-centric MCP tools."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.canvas.client import CanvasClient
from app.mcp.server import MCPServer, ToolDefinition


def _clean_payload(payload: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    return {k: v for k, v in (payload or {}).items() if v is not None}


async def _get_profile_handler(
    payload: Optional[Dict[str, Any]],
    client: CanvasClient,
) -> Dict[str, Any]:
    profile = await client.get_user_profile()
    return {"profile": profile}


async def _update_profile_handler(
    payload: Optional[Dict[str, Any]],
    client: CanvasClient,
) -> Dict[str, Any]:
    updates = _clean_payload(payload)
    if not updates:
        raise ValueError("At least one field is required to update the profile")
    profile = await client.update_user_profile(updates)
    return {"profile": profile}


USER_TOOLS: List[ToolDefinition] = [
    ToolDefinition(
        name="canvas_get_user_profile",
        description="Return the current Canvas user's profile information.",
        input_schema={"type": "object", "properties": {}, "additionalProperties": True},
        handler=_get_profile_handler,
    ),
    ToolDefinition(
        name="canvas_update_user_profile",
        description="Update one or more profile fields for the current user.",
        input_schema={
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "short_name": {"type": "string"},
                "bio": {"type": "string"},
                "title": {"type": "string"},
                "time_zone": {"type": "string"},
            },
            "additionalProperties": True,
        },
        handler=_update_profile_handler,
    ),
]


def register_user_tools(server: MCPServer) -> None:
    for tool in USER_TOOLS:
        server.register_tool(tool)


__all__ = ["USER_TOOLS", "register_user_tools"]
