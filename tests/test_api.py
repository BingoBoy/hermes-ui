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
    assert payload["allow_service_actions"] is False
    assert payload["capabilities"]["restart_hermes_gateway"] is False


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


def test_dashboard_returns_read_only_status_ui() -> None:
    response = client.get("/")

    assert response.status_code == 200
    body = response.text
    assert "Oppdater" in body
    assert "service-badge" in body
    assert "Teknisk JSON" in body
    assert "log-view" in body


def test_only_allowlisted_write_route_exists() -> None:
    forbidden_paths = {
        "/api/hermes/start",
        "/api/hermes/stop",
        "/api/terminal",
        "/api/shell",
        "/api/command",
    }
    forbidden_substrings = {"terminal", "shell", "command"}
    routes = [
        route
        for route in app.routes
        if getattr(route, "path", None)
        and not str(route.path).startswith(("/docs", "/redoc", "/openapi"))
    ]

    write_routes: list[tuple[str, set[str]]] = []
    for route in routes:
        methods = set(getattr(route, "methods", set()) or set())
        path = str(route.path)
        path_lower = path.lower()

        if methods - {"GET", "HEAD"}:
            write_routes.append((path, methods))

        assert path_lower not in forbidden_paths
        assert not any(term in path_lower for term in forbidden_substrings)

    assert write_routes == [("/api/hermes/restart", {"POST"})]

