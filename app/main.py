"""FastAPI application entrypoint and MCP bootstrap."""
from __future__ import annotations

from typing import Any, Dict

from fastapi import Depends, FastAPI, HTTPException, Path
from fastapi.responses import JSONResponse

from app.config import Settings, get_settings
from app.logging_config import configure_logging
from app.mcp.server import MCPServer, ToolInvocationRequest
from app.mcp.tools import register_all_tools


def create_app(settings: Settings | None = None) -> FastAPI:
    """Create and configure the FastAPI application."""

    app_settings = settings or get_settings()
    configure_logging(app_settings)

    mcp_server = MCPServer(settings=app_settings)
    register_all_tools(mcp_server)

    app = FastAPI(title="Canvas MCP Server", version="0.1.0")

    @app.on_event("startup")
    async def _startup() -> None:  # pragma: no cover - FastAPI lifecycle
        await mcp_server.start()

    @app.on_event("shutdown")
    async def _shutdown() -> None:  # pragma: no cover - FastAPI lifecycle
        await mcp_server.stop()

    @app.get("/healthz", tags=["health"])
    async def healthcheck(settings: Settings = Depends(lambda: app_settings)) -> Dict[str, str]:
        _ = settings
        return {"status": "ok"}

    @app.get("/mcp/tools", tags=["mcp"])
    async def list_tools() -> list[dict[str, Any]]:
        return mcp_server.list_tools()

    @app.post("/mcp/tools/{tool_name}", tags=["mcp"])
    async def invoke_tool(
        tool_name: str = Path(..., description="Name of the MCP tool to invoke"),
        payload: ToolInvocationRequest | None = None,
    ) -> JSONResponse:
        try:
            result = await mcp_server.invoke_tool(tool_name, payload.payload if payload else None)
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        return JSONResponse(content=result)

    return app


app = create_app()
