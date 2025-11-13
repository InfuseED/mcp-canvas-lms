"""Course-related MCP tools."""
from __future__ import annotations

from typing import Any, Dict, Optional

from app.canvas.client import CanvasClient
from app.mcp.server import MCPServer, ToolDefinition


def _clean_payload(payload: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    return {k: v for k, v in (payload or {}).items() if v is not None}


async def _list_courses_handler(payload: Optional[Dict[str, Any]], client: CanvasClient) -> Dict[str, Any]:
    data = dict(payload or {})
    include_ended = bool(data.pop("include_ended", False))
    courses = await client.list_courses(include_ended=include_ended, **_clean_payload(data))
    return {"courses": courses}


async def _get_course_handler(payload: Optional[Dict[str, Any]], client: CanvasClient) -> Dict[str, Any]:
    if not payload or "course_id" not in payload:
        raise ValueError("'course_id' is required")
    course = await client.get_course(int(payload["course_id"]))
    return {"course": course}


async def _create_course_handler(payload: Optional[Dict[str, Any]], client: CanvasClient) -> Dict[str, Any]:
    if not payload or "account_id" not in payload:
        raise ValueError("'account_id' is required")
    account_id = int(payload["account_id"])
    course_data = payload.get("course")
    if course_data is None:
        course_data = {k: v for k, v in payload.items() if k not in {"account_id"}}
    if not course_data:
        raise ValueError("Course data is required to create a course")
    course = await client.create_course(account_id, course_data)
    return {"course": course}


async def _update_course_handler(payload: Optional[Dict[str, Any]], client: CanvasClient) -> Dict[str, Any]:
    if not payload or "course_id" not in payload:
        raise ValueError("'course_id' is required")
    course_id = int(payload["course_id"])
    updates = payload.get("updates")
    if updates is None:
        updates = {k: v for k, v in payload.items() if k not in {"course_id"}}
    if not updates:
        raise ValueError("Update data is required")
    course = await client.update_course(course_id, updates)
    return {"course": course}


async def _delete_course_handler(payload: Optional[Dict[str, Any]], client: CanvasClient) -> Dict[str, Any]:
    if not payload or "course_id" not in payload:
        raise ValueError("'course_id' is required")
    course_id = int(payload["course_id"])
    result = await client.delete_course(course_id)
    return {"deleted": True, "details": result or {"course_id": course_id}}


COURSE_TOOLS = [
    ToolDefinition(
        name="canvas_list_courses",
        description="List courses visible to the authenticated Canvas user.",
        input_schema={
            "type": "object",
            "properties": {
                "include_ended": {
                    "type": "boolean",
                    "description": "Include courses that have already ended.",
                },
                "enrollment_state": {
                    "type": "string",
                    "description": "Filter by enrollment state (e.g., active, completed).",
                },
                "published": {
                    "type": "boolean",
                    "description": "Limit results to published courses.",
                },
                "search_term": {
                    "type": "string",
                    "description": "Search term applied to course name/code.",
                },
                "enrollment_type": {
                    "type": "string",
                    "description": "Enrollment type filter (e.g., teacher, student).",
                },
            },
            "additionalProperties": True,
            "required": [],
        },
        handler=_list_courses_handler,
    ),
    ToolDefinition(
        name="canvas_get_course",
        description="Retrieve full metadata for a single Canvas course.",
        input_schema={
            "type": "object",
            "properties": {
                "course_id": {"type": "number", "description": "Canvas course ID."},
            },
            "required": ["course_id"],
        },
        handler=_get_course_handler,
    ),
    ToolDefinition(
        name="canvas_create_course",
        description="Create a new Canvas course within the specified account.",
        input_schema={
            "type": "object",
            "properties": {
                "account_id": {"type": "number", "description": "Account ID that will own the course."},
                "course": {
                    "type": "object",
                    "description": "Canvas course attributes (name, course_code, start_at, etc.).",
                    "additionalProperties": True,
                },
            },
            "required": ["account_id"],
        },
        handler=_create_course_handler,
    ),
    ToolDefinition(
        name="canvas_update_course",
        description="Update core fields on an existing Canvas course.",
        input_schema={
            "type": "object",
            "properties": {
                "course_id": {"type": "number", "description": "Course to update."},
                "updates": {
                    "type": "object",
                    "description": "Course fields to update (name, syllabus_body, etc.).",
                    "additionalProperties": True,
                },
            },
            "required": ["course_id"],
        },
        handler=_update_course_handler,
    ),
    ToolDefinition(
        name="canvas_delete_course",
        description="Delete (or conclude) a Canvas course.",
        input_schema={
            "type": "object",
            "properties": {
                "course_id": {"type": "number", "description": "Course to delete."},
            },
            "required": ["course_id"],
        },
        handler=_delete_course_handler,
    ),
]


def register_course_tools(server: MCPServer) -> None:
    for tool in COURSE_TOOLS:
        server.register_tool(tool)


__all__ = ["COURSE_TOOLS", "register_course_tools"]
