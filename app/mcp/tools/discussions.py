"""Discussion-related MCP tools."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.canvas.client import CanvasClient
from app.mcp.server import MCPServer, ToolDefinition


def _clean_payload(payload: Optional[Dict[str, Any]], *exclude: str) -> Dict[str, Any]:
    excluded = set(exclude)
    return {k: v for k, v in (payload or {}).items() if k not in excluded and v is not None}


def _discussion_payload(payload: Optional[Dict[str, Any]], *exclude: str) -> Dict[str, Any]:
    if not payload:
        return {}
    if "discussion" in payload and isinstance(payload["discussion"], dict):
        return payload["discussion"]
    return _clean_payload(payload, *exclude)


async def _list_discussions_handler(payload: Optional[Dict[str, Any]], client: CanvasClient) -> Dict[str, Any]:
    if not payload or "course_id" not in payload:
        raise ValueError("'course_id' is required")
    course_id = int(payload["course_id"])
    params = _clean_payload(payload, "course_id")
    discussions = await client.list_discussions(course_id, **params)
    return {"discussions": discussions}


async def _get_discussion_handler(payload: Optional[Dict[str, Any]], client: CanvasClient) -> Dict[str, Any]:
    if not payload or "course_id" not in payload or "topic_id" not in payload:
        raise ValueError("'course_id' and 'topic_id' are required")
    course_id = int(payload["course_id"])
    topic_id = int(payload["topic_id"])
    params = _clean_payload(payload, "course_id", "topic_id")
    discussion = await client.get_discussion(course_id, topic_id, **params)
    return {"discussion": discussion}


async def _create_discussion_handler(payload: Optional[Dict[str, Any]], client: CanvasClient) -> Dict[str, Any]:
    if not payload or "course_id" not in payload:
        raise ValueError("'course_id' is required")
    course_id = int(payload["course_id"])
    discussion_payload = _discussion_payload(payload, "course_id")
    if not discussion_payload:
        raise ValueError("Discussion payload is required")
    discussion = await client.create_discussion(course_id, discussion_payload)
    return {"discussion": discussion}


async def _update_discussion_handler(payload: Optional[Dict[str, Any]], client: CanvasClient) -> Dict[str, Any]:
    if not payload or "course_id" not in payload or "topic_id" not in payload:
        raise ValueError("'course_id' and 'topic_id' are required")
    course_id = int(payload["course_id"])
    topic_id = int(payload["topic_id"])
    update_payload = payload.get("updates")
    if update_payload is None:
        update_payload = _discussion_payload(payload, "course_id", "topic_id")
    if not update_payload:
        raise ValueError("Discussion updates are required")
    discussion = await client.update_discussion(course_id, topic_id, update_payload)
    return {"discussion": discussion}


async def _delete_discussion_handler(payload: Optional[Dict[str, Any]], client: CanvasClient) -> Dict[str, Any]:
    if not payload or "course_id" not in payload or "topic_id" not in payload:
        raise ValueError("'course_id' and 'topic_id' are required")
    course_id = int(payload["course_id"])
    topic_id = int(payload["topic_id"])
    result = await client.delete_discussion(course_id, topic_id)
    return {"result": result or {"deleted": True}}


async def _list_entries_handler(payload: Optional[Dict[str, Any]], client: CanvasClient) -> Dict[str, Any]:
    if not payload or "course_id" not in payload or "topic_id" not in payload:
        raise ValueError("'course_id' and 'topic_id' are required")
    course_id = int(payload["course_id"])
    topic_id = int(payload["topic_id"])
    params = _clean_payload(payload, "course_id", "topic_id")
    entries = await client.list_discussion_entries(course_id, topic_id, **params)
    return {"entries": entries}


async def _create_entry_handler(payload: Optional[Dict[str, Any]], client: CanvasClient) -> Dict[str, Any]:
    if not payload or "course_id" not in payload or "topic_id" not in payload:
        raise ValueError("'course_id' and 'topic_id' are required")
    course_id = int(payload["course_id"])
    topic_id = int(payload["topic_id"])
    entry_payload = payload.get("entry") or _clean_payload(payload, "course_id", "topic_id", "entry")
    if not entry_payload:
        raise ValueError("Entry payload (message, attachment, etc.) is required")
    entry = await client.create_discussion_entry(course_id, topic_id, entry_payload)
    return {"entry": entry}


async def _list_replies_handler(payload: Optional[Dict[str, Any]], client: CanvasClient) -> Dict[str, Any]:
    if (
        not payload
        or "course_id" not in payload
        or "topic_id" not in payload
        or "entry_id" not in payload
    ):
        raise ValueError("'course_id', 'topic_id', and 'entry_id' are required")
    course_id = int(payload["course_id"])
    topic_id = int(payload["topic_id"])
    entry_id = int(payload["entry_id"])
    params = _clean_payload(payload, "course_id", "topic_id", "entry_id")
    replies = await client.list_discussion_replies(course_id, topic_id, entry_id, **params)
    return {"replies": replies}


async def _create_reply_handler(payload: Optional[Dict[str, Any]], client: CanvasClient) -> Dict[str, Any]:
    if (
        not payload
        or "course_id" not in payload
        or "topic_id" not in payload
        or "entry_id" not in payload
    ):
        raise ValueError("'course_id', 'topic_id', and 'entry_id' are required")
    course_id = int(payload["course_id"])
    topic_id = int(payload["topic_id"])
    entry_id = int(payload["entry_id"])
    reply_payload = payload.get("reply") or _clean_payload(
        payload,
        "course_id",
        "topic_id",
        "entry_id",
        "reply",
    )
    if not reply_payload:
        raise ValueError("Reply payload (message, attachment, etc.) is required")
    reply = await client.create_discussion_reply(course_id, topic_id, entry_id, reply_payload)
    return {"reply": reply}


DISCUSSION_TOOLS: List[ToolDefinition] = [
    ToolDefinition(
        name="canvas_list_discussion_topics",
        description="List discussion topics within a Canvas course.",
        input_schema={
            "type": "object",
            "properties": {
                "course_id": {"type": "number", "description": "Canvas course ID."},
            },
            "required": ["course_id"],
            "additionalProperties": True,
        },
        handler=_list_discussions_handler,
    ),
    ToolDefinition(
        name="canvas_list_discussions",
        description="List discussion topics within a Canvas course.",
        input_schema={
            "type": "object",
            "properties": {
                "course_id": {"type": "number"},
            },
            "required": ["course_id"],
            "additionalProperties": True,
        },
        handler=_list_discussions_handler,
    ),
    ToolDefinition(
        name="canvas_get_discussion_topic",
        description="Retrieve a Canvas discussion topic by ID.",
        input_schema={
            "type": "object",
            "properties": {
                "course_id": {"type": "number"},
                "topic_id": {"type": "number"},
            },
            "required": ["course_id", "topic_id"],
            "additionalProperties": True,
        },
        handler=_get_discussion_handler,
    ),
    ToolDefinition(
        name="canvas_get_discussion",
        description="Retrieve a Canvas discussion topic by ID.",
        input_schema={
            "type": "object",
            "properties": {
                "course_id": {"type": "number"},
                "topic_id": {"type": "number"},
            },
            "required": ["course_id", "topic_id"],
            "additionalProperties": True,
        },
        handler=_get_discussion_handler,
    ),
    ToolDefinition(
        name="canvas_create_discussion",
        description="Create a discussion topic within a Canvas course.",
        input_schema={
            "type": "object",
            "properties": {
                "course_id": {"type": "number"},
                "discussion": {
                    "type": "object",
                    "description": "Raw Canvas discussion payload (title, message, etc.).",
                    "additionalProperties": True,
                },
            },
            "required": ["course_id"],
            "additionalProperties": True,
        },
        handler=_create_discussion_handler,
    ),
    ToolDefinition(
        name="canvas_update_discussion",
        description="Update properties on an existing Canvas discussion topic.",
        input_schema={
            "type": "object",
            "properties": {
                "course_id": {"type": "number"},
                "topic_id": {"type": "number"},
                "updates": {
                    "type": "object",
                    "description": "Fields to update on the discussion topic.",
                    "additionalProperties": True,
                },
            },
            "required": ["course_id", "topic_id"],
            "additionalProperties": True,
        },
        handler=_update_discussion_handler,
    ),
    ToolDefinition(
        name="canvas_delete_discussion",
        description="Delete a Canvas discussion topic.",
        input_schema={
            "type": "object",
            "properties": {
                "course_id": {"type": "number"},
                "topic_id": {"type": "number"},
            },
            "required": ["course_id", "topic_id"],
        },
        handler=_delete_discussion_handler,
    ),
    ToolDefinition(
        name="canvas_list_discussion_entries",
        description="List entries (top-level posts) for a Canvas discussion topic.",
        input_schema={
            "type": "object",
            "properties": {
                "course_id": {"type": "number"},
                "topic_id": {"type": "number"},
            },
            "required": ["course_id", "topic_id"],
            "additionalProperties": True,
        },
        handler=_list_entries_handler,
    ),
    ToolDefinition(
        name="canvas_create_discussion_entry",
        description="Create a new entry in a Canvas discussion topic.",
        input_schema={
            "type": "object",
            "properties": {
                "course_id": {"type": "number"},
                "topic_id": {"type": "number"},
                "entry": {
                    "type": "object",
                    "description": "Entry payload containing message/attachments.",
                    "additionalProperties": True,
                },
                "message": {"type": "string", "description": "Convenience field for entry message."},
            },
            "required": ["course_id", "topic_id"],
            "additionalProperties": True,
        },
        handler=_create_entry_handler,
    ),
    ToolDefinition(
        name="canvas_post_to_discussion",
        description="Post a message to an existing discussion topic.",
        input_schema={
            "type": "object",
            "properties": {
                "course_id": {"type": "number"},
                "topic_id": {"type": "number"},
                "message": {"type": "string", "description": "Message content."},
            },
            "required": ["course_id", "topic_id", "message"],
        },
        handler=_create_entry_handler,
    ),
    ToolDefinition(
        name="canvas_list_discussion_replies",
        description="List replies to a specific discussion entry.",
        input_schema={
            "type": "object",
            "properties": {
                "course_id": {"type": "number"},
                "topic_id": {"type": "number"},
                "entry_id": {"type": "number"},
            },
            "required": ["course_id", "topic_id", "entry_id"],
            "additionalProperties": True,
        },
        handler=_list_replies_handler,
    ),
    ToolDefinition(
        name="canvas_create_discussion_reply",
        description="Post a reply to a discussion entry.",
        input_schema={
            "type": "object",
            "properties": {
                "course_id": {"type": "number"},
                "topic_id": {"type": "number"},
                "entry_id": {"type": "number"},
                "reply": {
                    "type": "object",
                    "description": "Reply payload (message, attachment, etc.).",
                    "additionalProperties": True,
                },
                "message": {"type": "string", "description": "Convenience field for reply message."},
            },
            "required": ["course_id", "topic_id", "entry_id"],
            "additionalProperties": True,
        },
        handler=_create_reply_handler,
    ),
]


def register_discussion_tools(server: MCPServer) -> None:
    for tool in DISCUSSION_TOOLS:
        server.register_tool(tool)


__all__ = ["DISCUSSION_TOOLS", "register_discussion_tools"]
