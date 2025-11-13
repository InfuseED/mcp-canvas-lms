"""Health MCP tool definition."""
from __future__ import annotations

from typing import Any, Dict, Optional

from app.canvas.client import CanvasClient
from app.mcp.server import MCPServer, ToolDefinition


async def _canvas_health_handler(
    payload: Optional[Dict[str, Any]], canvas_client: CanvasClient
) -> Dict[str, Any]:
    data = await canvas_client.health_check()
    return {"ok": True, "data": data}


def register_health_tool(server: MCPServer) -> None:
    tool = ToolDefinition(
        name="canvas_health_check",
        description="Checks Canvas API connectivity and returns basic status.",
        input_schema=None,
        handler=_canvas_health_handler,
    )
    server.register_tool(tool)


__all__ = ["register_health_tool"]
