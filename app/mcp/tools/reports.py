"""Account report tools."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.canvas.client import CanvasClient
from app.mcp.server import MCPServer, ToolDefinition


def _clean_payload(payload: Optional[Dict[str, Any]], *exclude: str) -> Dict[str, Any]:
    excluded = set(exclude)
    return {k: v for k, v in (payload or {}).items() if k not in excluded and v is not None}


async def _list_reports_handler(payload: Optional[Dict[str, Any]], client: CanvasClient) -> Dict[str, Any]:
    if not payload or "account_id" not in payload:
        raise ValueError("'account_id' is required")
    account_id = int(payload["account_id"])
    reports = await client.list_account_reports(account_id)
    return {"reports": reports}


async def _create_report_handler(payload: Optional[Dict[str, Any]], client: CanvasClient) -> Dict[str, Any]:
    if not payload or "account_id" not in payload or "report" not in payload:
        raise ValueError("'account_id' and 'report' are required")
    account_id = int(payload["account_id"])
    report = str(payload["report"])
    parameters = payload.get("parameters")
    report_obj = await client.create_account_report(account_id, report, parameters)
    return {"report": report_obj}


REPORT_TOOLS: List[ToolDefinition] = [
    ToolDefinition(
        name="canvas_get_account_reports",
        description="List available Canvas reports for an account.",
        input_schema={
            "type": "object",
            "properties": {"account_id": {"type": "number"}},
            "required": ["account_id"],
        },
        handler=_list_reports_handler,
    ),
    ToolDefinition(
        name="canvas_create_account_report",
        description="Kick off an account-level Canvas report.",
        input_schema={
            "type": "object",
            "properties": {
                "account_id": {"type": "number"},
                "report": {"type": "string", "description": "Report type (e.g., provisioning)."},
                "parameters": {
                    "type": "object",
                    "description": "Optional parameters forwarded to Canvas.",
                    "additionalProperties": True,
                },
            },
            "required": ["account_id", "report"],
        },
        handler=_create_report_handler,
    ),
]


def register_report_tools(server: MCPServer) -> None:
    for tool in REPORT_TOOLS:
        server.register_tool(tool)


__all__ = ["REPORT_TOOLS", "register_report_tools"]
