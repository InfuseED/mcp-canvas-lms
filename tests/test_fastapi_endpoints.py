from __future__ import annotations

from app.config import Settings
from app.main import create_app
from fastapi.testclient import TestClient
from profiles.profiles import PROFILES


def build_client(profile: str | None = None) -> TestClient:
    settings = Settings(
        canvas_base_url="https://canvas.example.com/api/v1",
        canvas_api_token="token",
        log_level="INFO",
        mcp_profile=profile,
    )
    app = create_app(settings)
    return TestClient(app)


def test_health_endpoint() -> None:
    with build_client() as client:
        response = client.get("/healthz")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


def test_admin_profile_lists_tools() -> None:
    with build_client() as client:
        response = client.get("/mcp/tools")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > len(PROFILES["builder"])


def test_readonly_profile_lists_expected_tools() -> None:
    with build_client(profile="readonly") as client:
        response = client.get("/mcp/tools")
        names = {tool["name"] for tool in response.json()}
        assert names == set(PROFILES["readonly"])


def test_builder_profile_lists_expected_tools() -> None:
    with build_client(profile="builder") as client:
        response = client.get("/mcp/tools")
        names = {tool["name"] for tool in response.json()}
        assert names == set(PROFILES["builder"])
