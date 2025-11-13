"""Application configuration via environment variables."""
from __future__ import annotations

from functools import lru_cache
from typing import Literal, Optional

from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration for the Canvas MCP server."""

    model_config = SettingsConfigDict(env_file=".env", env_prefix="", extra="ignore")

    canvas_base_url: AnyHttpUrl = Field(..., description="Base URL for the Canvas API")
    canvas_api_token: str = Field(..., description="Canvas API access token")
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO", description="Application log level"
    )
    mcp_profile: Optional[str] = Field(
        default=None,
        description="Optional MCP profile name that filters the exposed tool set",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached Settings instance."""

    return Settings()  # type: ignore[call-arg]


__all__ = ["Settings", "get_settings"]
