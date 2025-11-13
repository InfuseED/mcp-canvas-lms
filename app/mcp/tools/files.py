"""Canvas file and folder tools."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.canvas.client import CanvasClient
from app.mcp.server import MCPServer, ToolDefinition


def _clean_payload(payload: Optional[Dict[str, Any]], *exclude: str) -> Dict[str, Any]:
    excluded = set(exclude)
    return {k: v for k, v in (payload or {}).items() if k not in excluded and v is not None}


async def _list_files_handler(payload: Optional[Dict[str, Any]], client: CanvasClient) -> Dict[str, Any]:
    if not payload or "course_id" not in payload:
        raise ValueError("'course_id' is required")
    course_id = int(payload["course_id"])
    folder_id = payload.get("folder_id")
    folder = int(folder_id) if folder_id is not None else None
    params = _clean_payload(payload, "course_id", "folder_id")
    files = await client.list_files(course_id, folder_id=folder, **params)
    return {"files": files}


async def _get_file_handler(payload: Optional[Dict[str, Any]], client: CanvasClient) -> Dict[str, Any]:
    if not payload or "file_id" not in payload:
        raise ValueError("'file_id' is required")
    file_id = int(payload["file_id"])
    params = _clean_payload(payload, "file_id")
    file_data = await client.get_file(file_id, **params)
    return {"file": file_data}


async def _list_folders_handler(payload: Optional[Dict[str, Any]], client: CanvasClient) -> Dict[str, Any]:
    if not payload or "course_id" not in payload:
        raise ValueError("'course_id' is required")
    course_id = int(payload["course_id"])
    params = _clean_payload(payload, "course_id")
    folders = await client.list_folders(course_id, **params)
    return {"folders": folders}


FILE_TOOLS: List[ToolDefinition] = [
    ToolDefinition(
        name="canvas_list_files",
        description="List files for a Canvas course or a specific folder.",
        input_schema={
            "type": "object",
            "properties": {
                "course_id": {"type": "number", "description": "Canvas course ID."},
                "folder_id": {
                    "type": "number",
                    "description": "Optional Canvas folder ID to scope results.",
                },
            },
            "required": ["course_id"],
            "additionalProperties": True,
        },
        handler=_list_files_handler,
    ),
    ToolDefinition(
        name="canvas_get_file",
        description="Fetch metadata for a specific Canvas file.",
        input_schema={
            "type": "object",
            "properties": {"file_id": {"type": "number", "description": "Canvas file ID."}},
            "required": ["file_id"],
            "additionalProperties": True,
        },
        handler=_get_file_handler,
    ),
    ToolDefinition(
        name="canvas_list_folders",
        description="List folders within a Canvas course.",
        input_schema={
            "type": "object",
            "properties": {"course_id": {"type": "number", "description": "Canvas course ID."}},
            "required": ["course_id"],
            "additionalProperties": True,
        },
        handler=_list_folders_handler,
    ),
]


def register_file_tools(server: MCPServer) -> None:
    for tool in FILE_TOOLS:
        server.register_tool(tool)


__all__ = ["FILE_TOOLS", "register_file_tools"]
