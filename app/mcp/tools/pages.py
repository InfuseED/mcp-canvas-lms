"""Canvas page tools."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.canvas.client import CanvasClient
from app.mcp.server import MCPServer, ToolDefinition


def _clean_payload(payload: Optional[Dict[str, Any]], *exclude: str) -> Dict[str, Any]:
    excluded = set(exclude)
    return {k: v for k, v in (payload or {}).items() if k not in excluded and v is not None}


async def _list_pages_handler(payload: Optional[Dict[str, Any]], client: CanvasClient) -> Dict[str, Any]:
    if not payload or "course_id" not in payload:
        raise ValueError("'course_id' is required")
    course_id = int(payload["course_id"])
    params = _clean_payload(payload, "course_id")
    pages = await client.list_pages(course_id, **params)
    return {"pages": pages}


async def _get_page_handler(payload: Optional[Dict[str, Any]], client: CanvasClient) -> Dict[str, Any]:
    if not payload or "course_id" not in payload or "page_url" not in payload:
        raise ValueError("'course_id' and 'page_url' are required")
    course_id = int(payload["course_id"])
    page_url = str(payload["page_url"])
    params = _clean_payload(payload, "course_id", "page_url")
    page = await client.get_page(course_id, page_url, **params)
    return {"page": page}


PAGE_TOOLS: List[ToolDefinition] = [
    ToolDefinition(
        name="canvas_list_pages",
        description="List Canvas pages within a course.",
        input_schema={
            "type": "object",
            "properties": {"course_id": {"type": "number", "description": "Canvas course ID."}},
            "required": ["course_id"],
            "additionalProperties": True,
        },
        handler=_list_pages_handler,
    ),
    ToolDefinition(
        name="canvas_get_page",
        description="Retrieve a specific Canvas page by URL slug.",
        input_schema={
            "type": "object",
            "properties": {
                "course_id": {"type": "number"},
                "page_url": {"type": "string", "description": "Canvas page slug."},
            },
            "required": ["course_id", "page_url"],
            "additionalProperties": True,
        },
        handler=_get_page_handler,
    ),
]


def register_page_tools(server: MCPServer) -> None:
    for tool in PAGE_TOOLS:
        server.register_tool(tool)


__all__ = ["PAGE_TOOLS", "register_page_tools"]
