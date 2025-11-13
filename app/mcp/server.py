"""MCP server primitives for registering and invoking tools."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Awaitable, Callable, Dict, List, Optional

from profiles.profiles import PROFILES
from pydantic import BaseModel

from app.canvas.client import CanvasClient
from app.config import Settings

ToolHandlerFunc = Callable[[Optional[Dict[str, Any]], CanvasClient], Awaitable[Any]]


@dataclass
class ToolDefinition:
    name: str
    description: str
    input_schema: Optional[Dict[str, Any]] = None
    handler: ToolHandlerFunc = field(repr=False)


class ToolInvocationRequest(BaseModel):
    payload: Dict[str, Any]


class MCPServer:
    """Minimal registry for MCP tools."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client = CanvasClient(settings)
        self._registry: Dict[str, ToolDefinition] = {}

    async def start(self) -> None:
        await self._client.start()

    async def stop(self) -> None:
        await self._client.stop()

    def register_tool(self, tool: ToolDefinition) -> None:
        if tool.name in self._registry:
            raise ValueError(f"Tool '{tool.name}' already registered")
        self._registry[tool.name] = tool

    def list_tools(self) -> List[Dict[str, Any]]:
        allowed = self._allowed_tool_names()
        tools = [tool for name, tool in self._registry.items() if not allowed or name in allowed]
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.input_schema,
            }
            for tool in tools
        ]

    async def invoke_tool(
        self, tool_name: str, payload: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        allowed = self._allowed_tool_names()
        if allowed and tool_name not in allowed:
            raise ValueError(f"Tool '{tool_name}' is not available for the active profile")
        try:
            tool = self._registry[tool_name]
        except KeyError as exc:  # pragma: no cover - defensive
            raise ValueError(f"Tool '{tool_name}' is not registered") from exc
        return await tool.handler(payload, self._client)

    def _allowed_tool_names(self) -> Optional[set[str]]:
        profile = self._settings.mcp_profile
        if not profile:
            return None
        tool_names = PROFILES.get(profile)
        if not tool_names:
            return None
        if tool_names == ["*"]:
            return None
        return set(tool_names)


__all__ = ["MCPServer", "ToolDefinition", "ToolInvocationRequest"]
