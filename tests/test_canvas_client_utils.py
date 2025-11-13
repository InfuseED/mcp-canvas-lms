from __future__ import annotations

import httpx
import pytest
from app.canvas.client import CanvasClient
from app.config import Settings


@pytest.fixture()
def canvas_client() -> CanvasClient:
    settings = Settings(
        canvas_base_url="https://canvas.example.com/api/v1",
        canvas_api_token="token",
        log_level="INFO",
    )
    return CanvasClient(settings)


def test_parse_next_link_returns_url(canvas_client: CanvasClient) -> None:
    header = (
        '<https://canvas.example.com/api/v1/courses?page=2>; rel="next", '
        '<https://canvas.example.com/api/v1/courses?page=3>; rel="last"'
    )
    assert (
        canvas_client._parse_next_link(header)
        == "https://canvas.example.com/api/v1/courses?page=2"
    )


def test_parse_next_link_missing(canvas_client: CanvasClient) -> None:
    assert canvas_client._parse_next_link(None) is None
    assert (
        canvas_client._parse_next_link('<https://example.com>; rel="prev"') is None
    )


def test_decode_response_handles_json(canvas_client: CanvasClient) -> None:
    response = httpx.Response(
        200,
        json={"ok": True},
        request=httpx.Request("GET", "https://canvas.example.com"),
    )
    assert canvas_client._decode_response(response) == {"ok": True}


def test_decode_response_handles_text(canvas_client: CanvasClient) -> None:
    response = httpx.Response(
        200,
        text="plain text",
        headers={"content-type": "text/plain"},
        request=httpx.Request("GET", "https://canvas.example.com"),
    )
    assert canvas_client._decode_response(response) == {"raw": "plain text"}


def test_decode_response_handles_204(canvas_client: CanvasClient) -> None:
    response = httpx.Response(204, request=httpx.Request("GET", "https://canvas.example.com"))
    assert canvas_client._decode_response(response) == {}
