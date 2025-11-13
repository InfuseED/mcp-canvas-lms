"""Canvas quiz tools."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.canvas.client import CanvasClient
from app.mcp.server import MCPServer, ToolDefinition


def _clean_payload(payload: Optional[Dict[str, Any]], *exclude: str) -> Dict[str, Any]:
    excluded = set(exclude)
    return {k: v for k, v in (payload or {}).items() if k not in excluded and v is not None}


async def _list_quizzes_handler(payload: Optional[Dict[str, Any]], client: CanvasClient) -> Dict[str, Any]:
    if not payload or "course_id" not in payload:
        raise ValueError("'course_id' is required")
    course_id = int(payload["course_id"])
    params = _clean_payload(payload, "course_id")
    quizzes = await client.list_quizzes(course_id, **params)
    return {"quizzes": quizzes}


async def _get_quiz_handler(payload: Optional[Dict[str, Any]], client: CanvasClient) -> Dict[str, Any]:
    if not payload or "course_id" not in payload or "quiz_id" not in payload:
        raise ValueError("'course_id' and 'quiz_id' are required")
    course_id = int(payload["course_id"])
    quiz_id = int(payload["quiz_id"])
    params = _clean_payload(payload, "course_id", "quiz_id")
    quiz = await client.get_quiz(course_id, quiz_id, **params)
    return {"quiz": quiz}


async def _create_quiz_handler(payload: Optional[Dict[str, Any]], client: CanvasClient) -> Dict[str, Any]:
    if not payload or "course_id" not in payload:
        raise ValueError("'course_id' is required")
    course_id = int(payload["course_id"])
    quiz_payload = payload.get("quiz")
    if quiz_payload is None:
        quiz_payload = _clean_payload(payload, "course_id")
    if not quiz_payload:
        raise ValueError("Quiz configuration is required")
    quiz = await client.create_quiz(course_id, quiz_payload)
    return {"quiz": quiz}


async def _start_quiz_attempt_handler(payload: Optional[Dict[str, Any]], client: CanvasClient) -> Dict[str, Any]:
    if not payload or "course_id" not in payload or "quiz_id" not in payload:
        raise ValueError("'course_id' and 'quiz_id' are required")
    course_id = int(payload["course_id"])
    quiz_id = int(payload["quiz_id"])
    attempt = await client.start_quiz_attempt(course_id, quiz_id)
    return {"attempt": attempt}


QUIZ_TOOLS: List[ToolDefinition] = [
    ToolDefinition(
        name="canvas_list_quizzes",
        description="List Canvas quizzes for a course.",
        input_schema={
            "type": "object",
            "properties": {"course_id": {"type": "number", "description": "Canvas course ID."}},
            "required": ["course_id"],
            "additionalProperties": True,
        },
        handler=_list_quizzes_handler,
    ),
    ToolDefinition(
        name="canvas_get_quiz",
        description="Retrieve a single Canvas quiz by ID.",
        input_schema={
            "type": "object",
            "properties": {
                "course_id": {"type": "number"},
                "quiz_id": {"type": "number", "description": "Canvas quiz ID."},
            },
            "required": ["course_id", "quiz_id"],
            "additionalProperties": True,
        },
        handler=_get_quiz_handler,
    ),
    ToolDefinition(
        name="canvas_create_quiz",
        description="Create a new quiz within a Canvas course.",
        input_schema={
            "type": "object",
            "properties": {
                "course_id": {"type": "number"},
                "quiz": {
                    "type": "object",
                    "description": "Canvas quiz payload (title, description, etc.).",
                    "additionalProperties": True,
                },
                "title": {"type": "string"},
                "description": {"type": "string"},
                "quiz_type": {"type": "string"},
                "time_limit": {"type": "number"},
                "published": {"type": "boolean"},
                "due_at": {"type": "string"},
            },
            "required": ["course_id"],
            "additionalProperties": True,
        },
        handler=_create_quiz_handler,
    ),
    ToolDefinition(
        name="canvas_start_quiz_attempt",
        description="Start a new quiz attempt for the current user.",
        input_schema={
            "type": "object",
            "properties": {
                "course_id": {"type": "number"},
                "quiz_id": {"type": "number"},
            },
            "required": ["course_id", "quiz_id"],
        },
        handler=_start_quiz_attempt_handler,
    ),
]


def register_quiz_tools(server: MCPServer) -> None:
    for tool in QUIZ_TOOLS:
        server.register_tool(tool)


__all__ = ["QUIZ_TOOLS", "register_quiz_tools"]
