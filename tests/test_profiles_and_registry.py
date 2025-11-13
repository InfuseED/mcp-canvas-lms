from __future__ import annotations

from app.config import Settings
from app.mcp.server import MCPServer
from app.mcp.tools import register_all_tools
from profiles.profiles import PROFILES


def build_server(profile: str | None = None) -> MCPServer:
    settings = Settings(
        canvas_base_url="https://canvas.example.com/api/v1",
        canvas_api_token="token",
        log_level="INFO",
        mcp_profile=profile,
    )
    server = MCPServer(settings)
    register_all_tools(server)
    return server


def test_profile_lists_reference_registered_tools() -> None:
    server = build_server()
    registered = set(server._registry.keys())  # type: ignore[attr-defined]
    readonly = set(PROFILES["readonly"])
    builder = set(PROFILES["builder"])

    assert readonly <= registered
    assert builder <= registered
    assert readonly <= builder


def test_readonly_profile_filters_tools() -> None:
    server = build_server(profile="readonly")
    tool_names = {tool["name"] for tool in server.list_tools()}
    assert tool_names == set(PROFILES["readonly"])


def test_builder_profile_filters_tools() -> None:
    server = build_server(profile="builder")
    tool_names = {tool["name"] for tool in server.list_tools()}
    assert tool_names == set(PROFILES["builder"])


def test_admin_profile_exposes_all_tools() -> None:
    unfiltered_server = build_server()
    total = len(unfiltered_server._registry)  # type: ignore[attr-defined]

    admin_server = build_server(profile="admin")
    assert len(admin_server.list_tools()) == total
