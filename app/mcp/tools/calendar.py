"""Calendar and scheduling tools."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.canvas.client import CanvasClient
from app.mcp.server import MCPServer, ToolDefinition


def _clean_payload(payload: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    return {k: v for k, v in (payload or {}).items() if v is not None}


async def _list_calendar_events_handler(payload: Optional[Dict[str, Any]], client: CanvasClient) -> Dict[str, Any]:
    params = _clean_payload(payload)
    events = await client.list_calendar_events(**params)
    return {"events": events}


async def _get_upcoming_assignments_handler(payload: Optional[Dict[str, Any]], client: CanvasClient) -> Dict[str, Any]:
    params = dict(payload or {})
    limit = int(params.pop("limit", 10))
    events = await client.get_upcoming_assignments(limit=limit, **_clean_payload(params))
    return {"upcoming": events}


CALENDAR_TOOLS: List[ToolDefinition] = [
    ToolDefinition(
        name="canvas_list_calendar_events",
        description="List Canvas calendar events within an optional date range.",
        input_schema={
            "type": "object",
            "properties": {
                "start_date": {"type": "string", "description": "ISO8601 start date."},
                "end_date": {"type": "string", "description": "ISO8601 end date."},
                "type": {"type": "string", "description": "Canvas event type filter."},
            },
            "additionalProperties": True,
        },
        handler=_list_calendar_events_handler,
    ),
    ToolDefinition(
        name="canvas_get_upcoming_assignments",
        description="Return the current user's upcoming assignment events.",
        input_schema={
            "type": "object",
            "properties": {
                "limit": {"type": "number", "description": "Maximum events to return."},
            },
            "additionalProperties": True,
        },
        handler=_get_upcoming_assignments_handler,
    ),
]


def register_calendar_tools(server: MCPServer) -> None:
    for tool in CALENDAR_TOOLS:
        server.register_tool(tool)


__all__ = ["CALENDAR_TOOLS", "register_calendar_tools"]
