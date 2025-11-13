"""Conversation (Inbox) MCP tools."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.canvas.client import CanvasClient
from app.mcp.server import MCPServer, ToolDefinition


def _clean_payload(payload: Optional[Dict[str, Any]], *exclude: str) -> Dict[str, Any]:
    excluded = set(exclude)
    return {k: v for k, v in (payload or {}).items() if k not in excluded and v is not None}


def _require(payload: Optional[Dict[str, Any]], *fields: str) -> Dict[str, Any]:
    if not payload:
        raise ValueError(f"Fields {fields} are required")
    for field in fields:
        if field not in payload:
            raise ValueError(f"'{field}' is required")
    return payload


async def _list_conversations_handler(payload: Optional[Dict[str, Any]], client: CanvasClient) -> Dict[str, Any]:
    params = _clean_payload(payload)
    conversations = await client.list_conversations(**params)
    return {"conversations": conversations}


async def _get_conversation_handler(payload: Optional[Dict[str, Any]], client: CanvasClient) -> Dict[str, Any]:
    data = _require(payload, "conversation_id")
    conversation_id = int(data["conversation_id"])
    params = _clean_payload(payload, "conversation_id")
    conversation = await client.get_conversation(conversation_id, **params)
    return {"conversation": conversation}


async def _list_messages_handler(payload: Optional[Dict[str, Any]], client: CanvasClient) -> Dict[str, Any]:
    data = _require(payload, "conversation_id")
    conversation_id = int(data["conversation_id"])
    params = _clean_payload(payload, "conversation_id")
    messages = await client.list_conversation_messages(conversation_id, **params)
    return {"messages": messages}


async def _create_conversation_handler(payload: Optional[Dict[str, Any]], client: CanvasClient) -> Dict[str, Any]:
    data = _require(payload, "recipients", "body")
    recipients = data["recipients"]
    if not isinstance(recipients, list) or not recipients:
        raise ValueError("'recipients' must be a non-empty list")
    conversation_payload = payload.get("conversation")
    if conversation_payload is None:
        conversation_payload = _clean_payload(payload)
    conversation = await client.create_conversation(conversation_payload)
    return {"conversation": conversation}


async def _add_recipients_handler(payload: Optional[Dict[str, Any]], client: CanvasClient) -> Dict[str, Any]:
    data = _require(payload, "conversation_id", "recipients")
    conversation_id = int(data["conversation_id"])
    recipients = data["recipients"]
    if not isinstance(recipients, list) or not recipients:
        raise ValueError("'recipients' must be a non-empty list")
    updated = await client.add_conversation_recipients(conversation_id, recipients)
    return {"conversation": updated}


async def _send_message_handler(payload: Optional[Dict[str, Any]], client: CanvasClient) -> Dict[str, Any]:
    data = _require(payload, "conversation_id", "body")
    conversation_id = int(data["conversation_id"])
    message_payload = payload.get("message")
    if message_payload is None:
        message_payload = _clean_payload(payload, "conversation_id")
    sent = await client.send_conversation_message(conversation_id, message_payload)
    return {"message": sent}


async def _mark_read_handler(payload: Optional[Dict[str, Any]], client: CanvasClient) -> Dict[str, Any]:
    data = _require(payload, "conversation_id")
    conversation_id = int(data["conversation_id"])
    updated = await client.mark_conversation_read(conversation_id)
    return {"conversation": updated}


async def _delete_conversation_handler(payload: Optional[Dict[str, Any]], client: CanvasClient) -> Dict[str, Any]:
    data = _require(payload, "conversation_id")
    conversation_id = int(data["conversation_id"])
    result = await client.delete_conversation(conversation_id)
    return {"result": result or {"deleted": True}}


CONVERSATION_TOOLS: List[ToolDefinition] = [
    ToolDefinition(
        name="canvas_list_conversations",
        description="List Canvas inbox conversations for the current user.",
        input_schema={"type": "object", "additionalProperties": True},
        handler=_list_conversations_handler,
    ),
    ToolDefinition(
        name="canvas_get_conversation",
        description="Get details for a Canvas conversation.",
        input_schema={
            "type": "object",
            "properties": {"conversation_id": {"type": "number"}},
            "required": ["conversation_id"],
            "additionalProperties": True,
        },
        handler=_get_conversation_handler,
    ),
    ToolDefinition(
        name="canvas_list_conversation_messages",
        description="List messages for a Canvas conversation.",
        input_schema={
            "type": "object",
            "properties": {"conversation_id": {"type": "number"}},
            "required": ["conversation_id"],
            "additionalProperties": True,
        },
        handler=_list_messages_handler,
    ),
    ToolDefinition(
        name="canvas_create_conversation",
        description="Create a new Canvas conversation thread.",
        input_schema={
            "type": "object",
            "properties": {
                "recipients": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Recipient user IDs or logins.",
                },
                "body": {"type": "string", "description": "Message body."},
                "subject": {"type": "string", "description": "Conversation subject."},
                "context_code": {"type": "string", "description": "Context code for the conversation."},
            },
            "required": ["recipients", "body"],
            "additionalProperties": True,
        },
        handler=_create_conversation_handler,
    ),
    ToolDefinition(
        name="canvas_add_recipients",
        description="Add recipients to an existing Canvas conversation.",
        input_schema={
            "type": "object",
            "properties": {
                "conversation_id": {"type": "number"},
                "recipients": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Recipient user IDs or logins.",
                },
            },
            "required": ["conversation_id", "recipients"],
        },
        handler=_add_recipients_handler,
    ),
    ToolDefinition(
        name="canvas_send_conversation_message",
        description="Send a message within an existing Canvas conversation.",
        input_schema={
            "type": "object",
            "properties": {
                "conversation_id": {"type": "number"},
                "body": {"type": "string", "description": "Message body."},
            },
            "required": ["conversation_id", "body"],
            "additionalProperties": True,
        },
        handler=_send_message_handler,
    ),
    ToolDefinition(
        name="canvas_mark_conversation_read",
        description="Mark a conversation as read for the current user.",
        input_schema={
            "type": "object",
            "properties": {"conversation_id": {"type": "number"}},
            "required": ["conversation_id"],
        },
        handler=_mark_read_handler,
    ),
    ToolDefinition(
        name="canvas_delete_conversation",
        description="Delete a Canvas conversation (archive for the user).",
        input_schema={
            "type": "object",
            "properties": {"conversation_id": {"type": "number"}},
            "required": ["conversation_id"],
        },
        handler=_delete_conversation_handler,
    ),
]


def register_conversation_tools(server: MCPServer) -> None:
    for tool in CONVERSATION_TOOLS:
        server.register_tool(tool)


__all__ = ["CONVERSATION_TOOLS", "register_conversation_tools"]
