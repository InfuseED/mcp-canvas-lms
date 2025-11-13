"""Announcement MCP tools."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.canvas.client import CanvasClient
from app.mcp.server import MCPServer, ToolDefinition


def _clean_payload(payload: Optional[Dict[str, Any]], *exclude: str) -> Dict[str, Any]:
    excluded = set(exclude)
    return {k: v for k, v in (payload or {}).items() if k not in excluded and v is not None}


async def _list_announcements_handler(payload: Optional[Dict[str, Any]], client: CanvasClient) -> Dict[str, Any]:
    if payload and "context_codes" in payload:
        context_codes = payload["context_codes"]
        if not isinstance(context_codes, list) or not context_codes:
            raise ValueError("'context_codes' must be a non-empty list")
    elif payload and "course_id" in payload:
        context_codes = [f"course_{int(payload['course_id'])}"]
    else:
        raise ValueError("Either 'context_codes' or 'course_id' is required")
    params = _clean_payload(payload, "context_codes", "course_id")
    announcements = await client.list_announcements(context_codes, **params)
    return {"announcements": announcements}


async def _get_announcement_handler(payload: Optional[Dict[str, Any]], client: CanvasClient) -> Dict[str, Any]:
    if not payload or "course_id" not in payload or "topic_id" not in payload:
        raise ValueError("'course_id' and 'topic_id' are required")
    course_id = int(payload["course_id"])
    topic_id = int(payload["topic_id"])
    params = _clean_payload(payload, "course_id", "topic_id")
    announcement = await client.get_announcement(course_id, topic_id, **params)
    return {"announcement": announcement}


async def _create_announcement_handler(payload: Optional[Dict[str, Any]], client: CanvasClient) -> Dict[str, Any]:
    if not payload or "course_id" not in payload:
        raise ValueError("'course_id' is required")
    course_id = int(payload["course_id"])
    announcement_payload: Dict[str, Any]
    if "announcement" in payload and isinstance(payload["announcement"], dict):
        announcement_payload = dict(payload["announcement"])
    else:
        announcement_payload = _clean_payload(payload, "course_id")
    if not announcement_payload:
        raise ValueError("Announcement payload is required")
    announcement = await client.create_announcement(course_id, announcement_payload)
    return {"announcement": announcement}


ANNOUNCEMENT_TOOLS: List[ToolDefinition] = [
    ToolDefinition(
        name="canvas_list_announcements",
        description="List announcements using context codes or a course ID.",
        input_schema={
            "type": "object",
            "properties": {
                "context_codes": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Canvas context codes (e.g., course_123).",
                },
                "course_id": {
                    "type": "number",
                    "description": "Convenience parameter for single-course announcements.",
                },
            },
            "additionalProperties": True,
        },
        handler=_list_announcements_handler,
    ),
    ToolDefinition(
        name="canvas_get_announcement",
        description="Retrieve a single Canvas announcement by topic ID.",
        input_schema={
            "type": "object",
            "properties": {
                "course_id": {"type": "number"},
                "topic_id": {"type": "number"},
            },
            "required": ["course_id", "topic_id"],
            "additionalProperties": True,
        },
        handler=_get_announcement_handler,
    ),
    ToolDefinition(
        name="canvas_create_announcement",
        description="Create an announcement within a Canvas course.",
        input_schema={
            "type": "object",
            "properties": {
                "course_id": {"type": "number"},
                "announcement": {
                    "type": "object",
                    "description": "Raw Canvas announcement payload.",
                    "additionalProperties": True,
                },
                "title": {"type": "string", "description": "Announcement title."},
                "message": {"type": "string", "description": "Announcement body."},
            },
            "required": ["course_id"],
            "additionalProperties": True,
        },
        handler=_create_announcement_handler,
    ),
]


def register_announcement_tools(server: MCPServer) -> None:
    for tool in ANNOUNCEMENT_TOOLS:
        server.register_tool(tool)


__all__ = ["ANNOUNCEMENT_TOOLS", "register_announcement_tools"]
