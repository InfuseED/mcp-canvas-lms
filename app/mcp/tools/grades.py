"""Grade-related MCP tools."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.canvas.client import CanvasClient
from app.mcp.server import MCPServer, ToolDefinition


def _clean_payload(payload: Optional[Dict[str, Any]], *exclude: str) -> Dict[str, Any]:
    excluded = set(exclude)
    return {k: v for k, v in (payload or {}).items() if k not in excluded and v is not None}


async def _get_course_grades_handler(payload: Optional[Dict[str, Any]], client: CanvasClient) -> Dict[str, Any]:
    if not payload or "course_id" not in payload:
        raise ValueError("'course_id' is required")
    course_id = int(payload["course_id"])
    params = _clean_payload(payload, "course_id")
    enrollments = await client.get_course_grades(course_id, **params)
    return {"enrollments": enrollments}


async def _get_user_grades_handler(payload: Optional[Dict[str, Any]], client: CanvasClient) -> Dict[str, Any]:
    grades = await client.get_user_grades(**_clean_payload(payload))
    return {"grades": grades}


GRADE_TOOLS: List[ToolDefinition] = [
    ToolDefinition(
        name="canvas_get_course_grades",
        description="List enrollments (with grades) for a Canvas course.",
        input_schema={
            "type": "object",
            "properties": {
                "course_id": {"type": "number", "description": "Canvas course ID."},
                "include_inactive": {
                    "type": "boolean",
                    "description": "Include inactive enrollments.",
                },
            },
            "required": ["course_id"],
            "additionalProperties": True,
        },
        handler=_get_course_grades_handler,
    ),
    ToolDefinition(
        name="canvas_get_user_grades",
        description="Return all grades visible to the current Canvas user.",
        input_schema={"type": "object", "properties": {}, "additionalProperties": True},
        handler=_get_user_grades_handler,
    ),
]


def register_grade_tools(server: MCPServer) -> None:
    for tool in GRADE_TOOLS:
        server.register_tool(tool)


__all__ = ["GRADE_TOOLS", "register_grade_tools"]
