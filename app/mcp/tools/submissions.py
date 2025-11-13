"""Submission-related MCP tools."""
from __future__ import annotations

from typing import Any, Dict, Optional

from app.canvas.client import CanvasClient
from app.mcp.server import MCPServer, ToolDefinition


def _clean_payload(payload: Optional[Dict[str, Any]], *exclude: str) -> Dict[str, Any]:
    excluded = set(exclude)
    return {k: v for k, v in (payload or {}).items() if k not in excluded and v is not None}


async def _get_submission_handler(payload: Optional[Dict[str, Any]], client: CanvasClient) -> Dict[str, Any]:
    if not payload or "course_id" not in payload or "assignment_id" not in payload:
        raise ValueError("'course_id' and 'assignment_id' are required")
    course_id = int(payload["course_id"])
    assignment_id = int(payload["assignment_id"])
    user_id = payload.get("user_id", "self")
    params = _clean_payload(payload, "course_id", "assignment_id", "user_id")
    submission = await client.get_submission(course_id, assignment_id, user_id, **params)
    return {"submission": submission}


async def _submit_assignment_handler(payload: Optional[Dict[str, Any]], client: CanvasClient) -> Dict[str, Any]:
    if not payload or "course_id" not in payload or "assignment_id" not in payload:
        raise ValueError("'course_id' and 'assignment_id' are required")
    course_id = int(payload["course_id"])
    assignment_id = int(payload["assignment_id"])
    submission_payload = payload.get("submission")
    if submission_payload is None:
        submission_type = payload.get("submission_type")
        if not submission_type:
            raise ValueError("'submission_type' is required when no 'submission' payload is provided")
        submission_payload = {
            "submission_type": submission_type,
            **_clean_payload(payload, "course_id", "assignment_id", "submission_type"),
        }
    submission = await client.submit_assignment(course_id, assignment_id, submission_payload)
    return {"submission": submission}


async def _submit_grade_handler(
    payload: Optional[Dict[str, Any]],
    client: CanvasClient,
) -> Dict[str, Any]:
    if (
        not payload
        or "course_id" not in payload
        or "assignment_id" not in payload
        or "user_id" not in payload
    ):
        raise ValueError("'course_id', 'assignment_id', and 'user_id' are required")
    course_id = int(payload["course_id"])
    assignment_id = int(payload["assignment_id"])
    user_id = int(payload["user_id"])
    submission_payload = payload.get("submission")
    if submission_payload is None:
        if "grade" not in payload:
            raise ValueError("'grade' is required when no 'submission' payload is provided")
        submission_payload = {
            "posted_grade": payload["grade"],
        }
        if payload.get("comment"):
            submission_payload["comment"] = {"text_comment": payload["comment"]}
        submission_payload.update(
            _clean_payload(
                payload,
                "course_id",
                "assignment_id",
                "user_id",
                "grade",
                "comment",
            )
        )
    submission = await client.grade_submission(
        course_id,
        assignment_id,
        user_id,
        submission_payload,
    )
    return {"submission": submission}


SUBMISSION_TOOLS = [
    ToolDefinition(
        name="canvas_get_submission",
        description="Get submission details for a Canvas assignment.",
        input_schema={
            "type": "object",
            "properties": {
                "course_id": {"type": "number", "description": "Canvas course ID."},
                "assignment_id": {"type": "number", "description": "Assignment ID."},
                "user_id": {"type": ["number", "string"], "description": "User ID or 'self'."},
            },
            "required": ["course_id", "assignment_id"],
            "additionalProperties": True,
        },
        handler=_get_submission_handler,
    ),
    ToolDefinition(
        name="canvas_submit_assignment",
        description="Submit work for a Canvas assignment.",
        input_schema={
            "type": "object",
            "properties": {
                "course_id": {"type": "number", "description": "Canvas course ID."},
                "assignment_id": {"type": "number", "description": "Assignment ID."},
                "submission_type": {
                    "type": "string",
                    "description": "Submission type when not providing a raw payload.",
                },
                "body": {"type": "string", "description": "Text submission body."},
                "url": {"type": "string", "description": "URL for online_url submissions."},
                "file_ids": {
                    "type": "array",
                    "items": {"type": "number"},
                    "description": "Canvas file IDs for upload submissions.",
                },
                "submission": {
                    "type": "object",
                    "description": "Raw Canvas submission payload.",
                    "additionalProperties": True,
                },
            },
            "required": ["course_id", "assignment_id"],
            "additionalProperties": True,
        },
        handler=_submit_assignment_handler,
    ),
    ToolDefinition(
        name="canvas_submit_grade",
        description="Submit or update a grade for a Canvas submission.",
        input_schema={
            "type": "object",
            "properties": {
                "course_id": {"type": "number", "description": "Canvas course ID."},
                "assignment_id": {"type": "number", "description": "Assignment ID."},
                "user_id": {"type": "number", "description": "Student ID."},
                "grade": {
                    "oneOf": [{"type": "number"}, {"type": "string"}],
                    "description": "Grade to record when no raw submission payload is provided.",
                },
                "comment": {"type": "string", "description": "Optional submission comment."},
                "submission": {
                    "type": "object",
                    "description": "Raw Canvas submission payload for advanced grading scenarios.",
                    "additionalProperties": True,
                },
            },
            "required": ["course_id", "assignment_id", "user_id"],
            "additionalProperties": True,
        },
        handler=_submit_grade_handler,
    ),
]


def register_submission_tools(server: MCPServer) -> None:
    for tool in SUBMISSION_TOOLS:
        server.register_tool(tool)


__all__ = ["SUBMISSION_TOOLS", "register_submission_tools"]
