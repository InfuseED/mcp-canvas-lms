"""Canvas rubric tools."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.canvas.client import CanvasClient
from app.mcp.server import MCPServer, ToolDefinition


def _clean_payload(payload: Optional[Dict[str, Any]], *exclude: str) -> Dict[str, Any]:
    excluded = set(exclude)
    return {k: v for k, v in (payload or {}).items() if k not in excluded and v is not None}


async def _list_rubrics_handler(payload: Optional[Dict[str, Any]], client: CanvasClient) -> Dict[str, Any]:
    if not payload or "course_id" not in payload:
        raise ValueError("'course_id' is required")
    course_id = int(payload["course_id"])
    params = _clean_payload(payload, "course_id")
    rubrics = await client.list_rubrics(course_id, **params)
    return {"rubrics": rubrics}


async def _get_rubric_handler(payload: Optional[Dict[str, Any]], client: CanvasClient) -> Dict[str, Any]:
    if not payload or "course_id" not in payload or "rubric_id" not in payload:
        raise ValueError("'course_id' and 'rubric_id' are required")
    course_id = int(payload["course_id"])
    rubric_id = int(payload["rubric_id"])
    params = _clean_payload(payload, "course_id", "rubric_id")
    rubric = await client.get_rubric(course_id, rubric_id, **params)
    return {"rubric": rubric}


RUBRIC_TOOLS: List[ToolDefinition] = [
    ToolDefinition(
        name="canvas_list_rubrics",
        description="List rubrics available within a Canvas course.",
        input_schema={
            "type": "object",
            "properties": {"course_id": {"type": "number"}},
            "required": ["course_id"],
            "additionalProperties": True,
        },
        handler=_list_rubrics_handler,
    ),
    ToolDefinition(
        name="canvas_get_rubric",
        description="Retrieve a single rubric definition by ID.",
        input_schema={
            "type": "object",
            "properties": {
                "course_id": {"type": "number"},
                "rubric_id": {"type": "number"},
            },
            "required": ["course_id", "rubric_id"],
            "additionalProperties": True,
        },
        handler=_get_rubric_handler,
    ),
]


def register_rubric_tools(server: MCPServer) -> None:
    for tool in RUBRIC_TOOLS:
        server.register_tool(tool)


__all__ = ["RUBRIC_TOOLS", "register_rubric_tools"]
