"""Module-related MCP tools."""
from __future__ import annotations

from typing import Any, Dict, Optional

from app.canvas.client import CanvasClient
from app.mcp.server import MCPServer, ToolDefinition


def _clean_payload(payload: Optional[Dict[str, Any]], *exclude: str) -> Dict[str, Any]:
    excluded = set(exclude)
    return {k: v for k, v in (payload or {}).items() if k not in excluded and v is not None}


async def _list_modules_handler(payload: Optional[Dict[str, Any]], client: CanvasClient) -> Dict[str, Any]:
    if not payload or "course_id" not in payload:
        raise ValueError("'course_id' is required")
    course_id = int(payload["course_id"])
    params = _clean_payload(payload, "course_id")
    modules = await client.list_modules(course_id, **params)
    return {"modules": modules}


async def _get_module_handler(payload: Optional[Dict[str, Any]], client: CanvasClient) -> Dict[str, Any]:
    if not payload or "course_id" not in payload or "module_id" not in payload:
        raise ValueError("'course_id' and 'module_id' are required")
    course_id = int(payload["course_id"])
    module_id = int(payload["module_id"])
    params = _clean_payload(payload, "course_id", "module_id")
    module = await client.get_module(course_id, module_id, **params)
    return {"module": module}


async def _list_module_items_handler(payload: Optional[Dict[str, Any]], client: CanvasClient) -> Dict[str, Any]:
    if not payload or "course_id" not in payload or "module_id" not in payload:
        raise ValueError("'course_id' and 'module_id' are required")
    course_id = int(payload["course_id"])
    module_id = int(payload["module_id"])
    params = _clean_payload(payload, "course_id", "module_id")
    items = await client.list_module_items(course_id, module_id, **params)
    return {"module_items": items}


async def _get_module_item_handler(payload: Optional[Dict[str, Any]], client: CanvasClient) -> Dict[str, Any]:
    if (
        not payload
        or "course_id" not in payload
        or "module_id" not in payload
        or "item_id" not in payload
    ):
        raise ValueError("'course_id', 'module_id', and 'item_id' are required")
    course_id = int(payload["course_id"])
    module_id = int(payload["module_id"])
    item_id = int(payload["item_id"])
    params = _clean_payload(payload, "course_id", "module_id", "item_id")
    item = await client.get_module_item(course_id, module_id, item_id, **params)
    return {"module_item": item}


async def _mark_module_item_complete_handler(payload: Optional[Dict[str, Any]], client: CanvasClient) -> Dict[str, Any]:
    if (
        not payload
        or "course_id" not in payload
        or "module_id" not in payload
        or "item_id" not in payload
    ):
        raise ValueError("'course_id', 'module_id', and 'item_id' are required")
    course_id = int(payload["course_id"])
    module_id = int(payload["module_id"])
    item_id = int(payload["item_id"])
    result = await client.mark_module_item_complete(course_id, module_id, item_id)
    return {"completed": True, "details": result}


MODULE_TOOLS = [
    ToolDefinition(
        name="canvas_list_modules",
        description="List modules in a Canvas course.",
        input_schema={
            "type": "object",
            "properties": {
                "course_id": {"type": "number", "description": "Canvas course ID."},
            },
            "required": ["course_id"],
            "additionalProperties": True,
        },
        handler=_list_modules_handler,
    ),
    ToolDefinition(
        name="canvas_get_module",
        description="Retrieve details for a single Canvas module.",
        input_schema={
            "type": "object",
            "properties": {
                "course_id": {"type": "number", "description": "Canvas course ID."},
                "module_id": {"type": "number", "description": "Module ID."},
            },
            "required": ["course_id", "module_id"],
            "additionalProperties": True,
        },
        handler=_get_module_handler,
    ),
    ToolDefinition(
        name="canvas_list_module_items",
        description="List the items that belong to a Canvas module.",
        input_schema={
            "type": "object",
            "properties": {
                "course_id": {"type": "number", "description": "Canvas course ID."},
                "module_id": {"type": "number", "description": "Module ID."},
            },
            "required": ["course_id", "module_id"],
            "additionalProperties": True,
        },
        handler=_list_module_items_handler,
    ),
    ToolDefinition(
        name="canvas_get_module_item",
        description="Get metadata for a Canvas module item.",
        input_schema={
            "type": "object",
            "properties": {
                "course_id": {"type": "number", "description": "Canvas course ID."},
                "module_id": {"type": "number", "description": "Module ID."},
                "item_id": {"type": "number", "description": "Module item ID."},
            },
            "required": ["course_id", "module_id", "item_id"],
            "additionalProperties": True,
        },
        handler=_get_module_item_handler,
    ),
    ToolDefinition(
        name="canvas_mark_module_item_complete",
        description="Mark a Canvas module item as complete for the authenticated user.",
        input_schema={
            "type": "object",
            "properties": {
                "course_id": {"type": "number", "description": "Canvas course ID."},
                "module_id": {"type": "number", "description": "Module ID."},
                "item_id": {"type": "number", "description": "Module item ID."},
            },
            "required": ["course_id", "module_id", "item_id"],
        },
        handler=_mark_module_item_complete_handler,
    ),
]


def register_module_tools(server: MCPServer) -> None:
    for tool in MODULE_TOOLS:
        server.register_tool(tool)


__all__ = ["MODULE_TOOLS", "register_module_tools"]
