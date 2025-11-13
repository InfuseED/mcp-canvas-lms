"""Enrollment-related MCP tools."""
from __future__ import annotations

from typing import Any, Dict, Optional

from app.canvas.client import CanvasClient
from app.mcp.server import MCPServer, ToolDefinition


async def _list_enrollments_handler(payload: Optional[Dict[str, Any]], client: CanvasClient) -> Dict[str, Any]:
    if not payload or "course_id" not in payload:
        raise ValueError("'course_id' is required")
    course_id = int(payload["course_id"])
    filters = {k: v for k, v in (payload or {}).items() if k != "course_id" and v is not None}
    enrollments = await client.list_enrollments(course_id, **filters)
    return {"enrollments": enrollments}


async def _enroll_user_handler(payload: Optional[Dict[str, Any]], client: CanvasClient) -> Dict[str, Any]:
    if not payload or "course_id" not in payload:
        raise ValueError("'course_id' is required")
    if "user_id" not in payload:
        raise ValueError("'user_id' is required")
    course_id = int(payload["course_id"])
    enrollment_payload = payload.get("enrollment")
    if enrollment_payload is None:
        enrollment_payload = {
            "user_id": payload["user_id"],
            "type": payload.get("role", payload.get("type", "StudentEnrollment")),
            "enrollment_state": payload.get("enrollment_state", "active"),
            "notify": payload.get("notify_users", False),
        }
    enroll = await client.enroll_user(course_id, enrollment_payload)
    return {"enrollment": enroll}


async def _conclude_enrollment_handler(payload: Optional[Dict[str, Any]], client: CanvasClient) -> Dict[str, Any]:
    if not payload or "course_id" not in payload or "enrollment_id" not in payload:
        raise ValueError("'course_id' and 'enrollment_id' are required")
    course_id = int(payload["course_id"])
    enrollment_id = int(payload["enrollment_id"])
    result = await client.conclude_enrollment(course_id, enrollment_id)
    return {"concluded": True, "details": result or {"course_id": course_id, "enrollment_id": enrollment_id}}


ENROLLMENT_TOOLS = [
    ToolDefinition(
        name="canvas_list_enrollments",
        description="List enrollments for a specific Canvas course.",
        input_schema={
            "type": "object",
            "properties": {
                "course_id": {"type": "number", "description": "Course whose enrollments should be listed."},
                "type": {
                    "type": "string",
                    "description": "Filter by enrollment type (TeacherEnrollment, StudentEnrollment, etc.).",
                },
                "state": {
                    "type": "string",
                    "description": "Enrollment state filter (active, invited, completed, etc.).",
                },
                "role": {
                    "type": "string",
                    "description": "Role to filter by when retrieving enrollments.",
                },
            },
            "required": ["course_id"],
            "additionalProperties": True,
        },
        handler=_list_enrollments_handler,
    ),
    ToolDefinition(
        name="canvas_enroll_user",
        description="Create or update an enrollment for a user in a Canvas course.",
        input_schema={
            "type": "object",
            "properties": {
                "course_id": {"type": "number", "description": "Course to enroll the user in."},
                "user_id": {"type": "number", "description": "Canvas user ID."},
                "role": {
                    "type": "string",
                    "description": "Role of the enrollment (StudentEnrollment, TeacherEnrollment, etc.).",
                },
                "enrollment_state": {
                    "type": "string",
                    "description": "Initial enrollment state (active, invited, etc.).",
                },
                "notify_users": {
                    "type": "boolean",
                    "description": "Send Canvas notification emails to the user.",
                },
                "enrollment": {
                    "type": "object",
                    "description": "Raw Canvas enrollment payload (advanced usage).",
                    "additionalProperties": True,
                },
            },
            "required": ["course_id", "user_id"],
        },
        handler=_enroll_user_handler,
    ),
    ToolDefinition(
        name="canvas_conclude_enrollment",
        description="Conclude (unenroll) a user from a Canvas course.",
        input_schema={
            "type": "object",
            "properties": {
                "course_id": {"type": "number", "description": "Course ID."},
                "enrollment_id": {"type": "number", "description": "Enrollment ID returned by Canvas."},
            },
            "required": ["course_id", "enrollment_id"],
        },
        handler=_conclude_enrollment_handler,
    ),
]


def register_enrollment_tools(server: MCPServer) -> None:
    for tool in ENROLLMENT_TOOLS:
        server.register_tool(tool)


__all__ = ["ENROLLMENT_TOOLS", "register_enrollment_tools"]
