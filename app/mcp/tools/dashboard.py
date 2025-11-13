"""Dashboard-centric tools."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.canvas.client import CanvasClient
from app.mcp.server import MCPServer, ToolDefinition


def _clean_payload(payload: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    return {k: v for k, v in (payload or {}).items() if v is not None}


async def _get_dashboard_handler(payload: Optional[Dict[str, Any]], client: CanvasClient) -> Dict[str, Any]:
    dashboard = await client.get_dashboard(**_clean_payload(payload))
    return {"dashboard": dashboard}


async def _get_dashboard_cards_handler(payload: Optional[Dict[str, Any]], client: CanvasClient) -> Dict[str, Any]:
    cards = await client.get_dashboard_cards(**_clean_payload(payload))
    return {"cards": cards}


DASHBOARD_TOOLS: List[ToolDefinition] = [
    ToolDefinition(
        name="canvas_get_dashboard",
        description="Return the Canvas dashboard payload for the current user.",
        input_schema={"type": "object", "properties": {}, "additionalProperties": True},
        handler=_get_dashboard_handler,
    ),
    ToolDefinition(
        name="canvas_get_dashboard_cards",
        description="List dashboard cards (course tiles) for the current user.",
        input_schema={"type": "object", "properties": {}, "additionalProperties": True},
        handler=_get_dashboard_cards_handler,
    ),
]


def register_dashboard_tools(server: MCPServer) -> None:
    for tool in DASHBOARD_TOOLS:
        server.register_tool(tool)


__all__ = ["DASHBOARD_TOOLS", "register_dashboard_tools"]
