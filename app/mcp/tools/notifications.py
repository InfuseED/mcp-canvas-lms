"""Canvas notification tools."""
from __future__ import annotations

from typing import Dict, List, Optional

from app.canvas.client import CanvasClient
from app.mcp.server import MCPServer, ToolDefinition


def _clean_payload(payload: Optional[Dict[str, object]]) -> Dict[str, object]:
    return {k: v for k, v in (payload or {}).items() if v is not None}


async def _list_notifications_handler(payload: Optional[Dict[str, object]], client: CanvasClient) -> Dict[str, object]:
    notifications = await client.list_notifications(**_clean_payload(payload))
    return {"notifications": notifications}


NOTIFICATION_TOOLS: List[ToolDefinition] = [
    ToolDefinition(
        name="canvas_list_notifications",
        description="Return the authenticated user's Canvas activity stream entries.",
        input_schema={"type": "object", "properties": {}, "additionalProperties": True},
        handler=_list_notifications_handler,
    ),
]


def register_notification_tools(server: MCPServer) -> None:
    for tool in NOTIFICATION_TOOLS:
        server.register_tool(tool)


__all__ = ["NOTIFICATION_TOOLS", "register_notification_tools"]
