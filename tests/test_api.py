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
    assert payload["allow_bob_tasks"] is False
    assert payload["bob_task_assignee"] is None
    assert payload["bob_task_assignee_configured"] is False
    assert payload["bob_task_assignee_valid"] is True
    assert payload["capabilities"]["restart_hermes_gateway"] is False
    assert payload["capabilities"]["create_bob_task"] is False
    assert payload["capabilities"]["list_bob_tasks"] is False
    assert payload["capabilities"]["show_bob_task"] is False


def test_api_status_reports_server_controlled_bob_task_assignee(
    monkeypatch,
) -> None:
    monkeypatch.setenv("HERMES_BOB_TASK_ASSIGNEE", "default")

    response = client.get("/api/status")

    assert response.status_code == 200
    payload = response.json()
    assert payload["bob_task_assignee"] == "default"
    assert payload["bob_task_assignee_configured"] is True
    assert payload["bob_task_assignee_valid"] is True


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


def test_dashboard_includes_bob_task_history_ui() -> None:
    response = client.get("/")

    assert response.status_code == 200
    body = response.text
    assert "bob-history-section" in body
    assert "Bob-oppgaver" in body
    assert "bob-history-refresh" in body
    assert "bob-auto-refresh-toggle" in body
    assert "Auto-oppdater oppgaver" in body
    assert "status-pill.completed" in body
    assert "normalizeBobStatus" in body


def test_dashboard_includes_bob_inbox_ui() -> None:
    response = client.get("/")

    assert response.status_code == 200
    body = response.text
    assert "bob-inbox-section" in body
    assert "Bob Inbox" in body
    assert "bob-inbox-list-wrap" in body
    assert "Ingen ferdige Bob-resultater ennå" in body
    assert "renderBobInbox" in body


def test_dashboard_includes_bob_result_actions_ui() -> None:
    response = client.get("/")

    assert response.status_code == 200
    body = response.text
    assert "copyTextToClipboard" in body
    assert "taskResultValue" in body
    assert "latest_summary" in body
    assert "Kopier resultat" in body
    assert "Kopier ID" in body
    assert "Kopier tittel" in body
    assert "Kunne ikke kopiere" in body
    assert "Vis mer" in body
    assert "Vis mindre" in body
    assert "bob-detail-result-toolbar" in body
    assert "bindResultExpandToggle" in body


def test_dashboard_includes_bob_task_submission_ui() -> None:
    response = client.get("/")

    assert response.status_code == 200
    body = response.text
    assert "bob-task-section" in body
    assert "Send oppgave til Bob" in body
    assert "bob-task-form" in body
    assert "asynkron kanban" in body


def test_dashboard_includes_bob_task_templates_ui() -> None:
    response = client.get("/")

    assert response.status_code == 200
    body = response.text
    assert "bob-task-templates" in body
    assert "Bob task-maler" in body
    assert "BOB_TASK_TEMPLATES" in body
    assert "submitBobTaskPayload" in body
    assert "sendBobTaskTemplate" in body
    assert "buildBobTaskTemplatePayload" in body
    assert "Morgenbrief" in body
    assert "Markedsføringsstatus" in body
    assert 'data-template-id="morgenbrief"' in body
    assert "Send mal til Bob" in body
    assert "bob-template-input-morgenbrief" in body
    assert "Fokus for dagen" in body
    assert "URL som skal analyseres" in body
    assert "Konkurrent eller tema" in body
    assert "Periode" in body
    assert "Fokusområde" in body
    assert "Oppgave sendt til Bob" in body


def test_dashboard_includes_restart_confirmation_ui() -> None:
    response = client.get("/")

    assert response.status_code == 200
    body = response.text
    assert "restart-btn" in body
    assert "restart-modal" in body
    assert "Bekreft restart" in body


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

    assert sorted(write_routes) == [
        ("/api/bob/tasks", {"POST"}),
        ("/api/hermes/restart", {"POST"}),
    ]
