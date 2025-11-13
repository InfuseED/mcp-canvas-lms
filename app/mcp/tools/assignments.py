"""Assignment-related MCP tools."""
from __future__ import annotations

from typing import Any, Dict, Optional

from app.canvas.client import CanvasClient
from app.mcp.server import MCPServer, ToolDefinition


def _clean_payload(payload: Optional[Dict[str, Any]], *exclude: str) -> Dict[str, Any]:
    excluded = set(exclude)
    return {k: v for k, v in (payload or {}).items() if k not in excluded and v is not None}


async def _list_assignments_handler(payload: Optional[Dict[str, Any]], client: CanvasClient) -> Dict[str, Any]:
    if not payload or "course_id" not in payload:
        raise ValueError("'course_id' is required")
    course_id = int(payload["course_id"])
    include_submissions = bool(payload.get("include_submissions", False))
    filters = _clean_payload(payload, "course_id", "include_submissions")
    assignments = await client.list_assignments(
        course_id,
        include_submissions=include_submissions,
        **filters,
    )
    return {"assignments": assignments}


async def _get_assignment_handler(payload: Optional[Dict[str, Any]], client: CanvasClient) -> Dict[str, Any]:
    if not payload or "course_id" not in payload or "assignment_id" not in payload:
        raise ValueError("'course_id' and 'assignment_id' are required")
    course_id = int(payload["course_id"])
    assignment_id = int(payload["assignment_id"])
    include_submission = bool(payload.get("include_submission", False))
    params = _clean_payload(payload, "course_id", "assignment_id", "include_submission")
    assignment = await client.get_assignment(
        course_id,
        assignment_id,
        include_submission=include_submission,
        **params,
    )
    return {"assignment": assignment}


async def _create_assignment_handler(payload: Optional[Dict[str, Any]], client: CanvasClient) -> Dict[str, Any]:
    if not payload or "course_id" not in payload:
        raise ValueError("'course_id' is required")
    course_id = int(payload["course_id"])
    assignment_payload = payload.get("assignment")
    if assignment_payload is None:
        assignment_payload = _clean_payload(payload, "course_id")
    if not assignment_payload:
        raise ValueError("Assignment payload is required")
    assignment = await client.create_assignment(course_id, assignment_payload)
    return {"assignment": assignment}


async def _update_assignment_handler(payload: Optional[Dict[str, Any]], client: CanvasClient) -> Dict[str, Any]:
    if not payload or "course_id" not in payload or "assignment_id" not in payload:
        raise ValueError("'course_id' and 'assignment_id' are required")
    course_id = int(payload["course_id"])
    assignment_id = int(payload["assignment_id"])
    updates = payload.get("updates")
    if updates is None:
        updates = _clean_payload(payload, "course_id", "assignment_id")
    if not updates:
        raise ValueError("Assignment updates are required")
    assignment = await client.update_assignment(course_id, assignment_id, updates)
    return {"assignment": assignment}


async def _list_assignment_groups_handler(payload: Optional[Dict[str, Any]], client: CanvasClient) -> Dict[str, Any]:
    if not payload or "course_id" not in payload:
        raise ValueError("'course_id' is required")
    course_id = int(payload["course_id"])
    params = _clean_payload(payload, "course_id")
    groups = await client.list_assignment_groups(course_id, **params)
    return {"assignment_groups": groups}


ASSIGNMENT_TOOLS = [
    ToolDefinition(
        name="canvas_list_assignments",
        description="List assignments for a Canvas course with optional filters.",
        input_schema={
            "type": "object",
            "properties": {
                "course_id": {"type": "number", "description": "Canvas course ID."},
                "include_submissions": {
                    "type": "boolean",
                    "description": "Include submission data for each assignment.",
                },
                "bucket": {"type": "string", "description": "Canvas assignment bucket filter."},
                "search_term": {"type": "string", "description": "Filter assignments by search term."},
                "include": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Additional Canvas includes to request.",
                },
            },
            "required": ["course_id"],
            "additionalProperties": True,
        },
        handler=_list_assignments_handler,
    ),
    ToolDefinition(
        name="canvas_get_assignment",
        description="Retrieve a single Canvas assignment.",
        input_schema={
            "type": "object",
            "properties": {
                "course_id": {"type": "number", "description": "Canvas course ID."},
                "assignment_id": {"type": "number", "description": "Assignment identifier."},
                "include_submission": {
                    "type": "boolean",
                    "description": "Include the authenticated user's submission.",
                },
            },
            "required": ["course_id", "assignment_id"],
            "additionalProperties": True,
        },
        handler=_get_assignment_handler,
    ),
    ToolDefinition(
        name="canvas_create_assignment",
        description="Create a Canvas assignment within the specified course.",
        input_schema={
            "type": "object",
            "properties": {
                "course_id": {"type": "number", "description": "Course that will own the assignment."},
                "assignment": {
                    "type": "object",
                    "description": "Raw Canvas assignment payload (name, due_at, etc.).",
                    "additionalProperties": True,
                },
            },
            "required": ["course_id"],
            "additionalProperties": True,
        },
        handler=_create_assignment_handler,
    ),
    ToolDefinition(
        name="canvas_update_assignment",
        description="Update core fields on an existing Canvas assignment.",
        input_schema={
            "type": "object",
            "properties": {
                "course_id": {"type": "number", "description": "Course that owns the assignment."},
                "assignment_id": {"type": "number", "description": "Assignment identifier."},
                "updates": {
                    "type": "object",
                    "description": "Fields to update on the assignment.",
                    "additionalProperties": True,
                },
            },
            "required": ["course_id", "assignment_id"],
            "additionalProperties": True,
        },
        handler=_update_assignment_handler,
    ),
    ToolDefinition(
        name="canvas_list_assignment_groups",
        description="List assignment groups for a Canvas course.",
        input_schema={
            "type": "object",
            "properties": {
                "course_id": {"type": "number", "description": "Canvas course ID."},
            },
            "required": ["course_id"],
            "additionalProperties": True,
        },
        handler=_list_assignment_groups_handler,
    ),
]


def register_assignment_tools(server: MCPServer) -> None:
    for tool in ASSIGNMENT_TOOLS:
        server.register_tool(tool)


__all__ = ["ASSIGNMENT_TOOLS", "register_assignment_tools"]
