"""Canvas-specific exception hierarchy."""
from __future__ import annotations

from typing import Any, Optional


class CanvasError(Exception):
    """Base exception for Canvas client errors."""


class CanvasAPIError(CanvasError):
    """Represents a non-success response from the Canvas API."""

    def __init__(self, message: str, status_code: int, payload: Optional[Any] = None) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.payload = payload

    def to_dict(self) -> dict[str, Any]:
        return {"message": str(self), "status_code": self.status_code, "payload": self.payload}


__all__ = ["CanvasAPIError", "CanvasError"]
