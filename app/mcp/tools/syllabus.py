"""Canvas syllabus tool."""
from __future__ import annotations

from typing import Dict, List, Optional

from app.canvas.client import CanvasClient
from app.mcp.server import MCPServer, ToolDefinition


def _clean_payload(payload: Optional[Dict[str, object]]) -> Dict[str, object]:
    return {k: v for k, v in (payload or {}).items() if v is not None}


async def _get_syllabus_handler(
    payload: Optional[Dict[str, object]],
    client: CanvasClient,
) -> Dict[str, object]:
    if not payload or "course_id" not in payload:
        raise ValueError("'course_id' is required")
    course_id = int(payload["course_id"])
    syllabus = await client.get_syllabus(course_id)
    return {"syllabus": syllabus}


SYLLABUS_TOOLS: List[ToolDefinition] = [
    ToolDefinition(
        name="canvas_get_syllabus",
        description="Return the syllabus body for a Canvas course.",
        input_schema={
            "type": "object",
            "properties": {"course_id": {"type": "number", "description": "Canvas course ID."}},
            "required": ["course_id"],
        },
        handler=_get_syllabus_handler,
    ),
]


def register_syllabus_tools(server: MCPServer) -> None:
    for tool in SYLLABUS_TOOLS:
        server.register_tool(tool)


__all__ = ["SYLLABUS_TOOLS", "register_syllabus_tools"]
