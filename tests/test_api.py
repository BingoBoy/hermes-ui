from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_api_status_returns_read_only_service_status() -> None:
    response = client.get("/api/status")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["service"] == "hermes-ui"
    assert payload["bind_host"] == "127.0.0.1"
    assert payload["bind_port"] == 8787
    assert payload["read_only"] is True
    assert payload["allow_unsafe_commands"] is False


def test_api_system_returns_safe_system_payload() -> None:
    response = client.get("/api/system")

    assert response.status_code == 200
    payload = response.json()
    assert "hostname" in payload
    assert "disk" in payload
    assert "memory" in payload
    assert "checked_at" in payload


def test_api_hermes_status_fails_safely() -> None:
    response = client.get("/api/hermes/status")

    assert response.status_code == 200
    payload = response.json()
    assert payload["service"] == "hermes"
    assert payload["read_only"] is True
    assert "running" in payload
    assert "launchctl" in payload
    assert "process" in payload


def test_no_write_action_routes_exist() -> None:
    forbidden_terms = {"start", "stop", "restart", "logs", "terminal", "shell", "command"}
    routes = [
        route
        for route in app.routes
        if getattr(route, "path", None)
        and not str(route.path).startswith(("/docs", "/redoc", "/openapi"))
    ]

    for route in routes:
        methods = getattr(route, "methods", set())
        path = str(route.path).lower()
        assert methods <= {"GET", "HEAD"}
        assert not any(term in path for term in forbidden_terms)

