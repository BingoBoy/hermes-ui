"""Tests for read-only operations status."""

from __future__ import annotations

import plistlib
from pathlib import Path

from fastapi.testclient import TestClient

from backend.config import Settings
from backend.main import app
from backend.operations import get_operations_status

client = TestClient(app)


def test_api_operations_returns_launch_agents() -> None:
    response = client.get("/api/operations")

    assert response.status_code == 200
    payload = response.json()
    assert payload["read_only"] is True
    assert len(payload["launch_agents"]) == 2
    ids = {agent["id"] for agent in payload["launch_agents"]}
    assert ids == {"hermes-ui", "hermes-gateway"}
    assert payload["docker"]["included"] is False
    assert "checked_at" in payload


def test_operations_never_returns_environment_values(
    tmp_path: Path, monkeypatch,
) -> None:
    plist_path = tmp_path / "test-agent.plist"
    plist_path.write_bytes(
        plistlib.dumps(
            {
                "Label": "test.agent",
                "ProgramArguments": ["/bin/echo", "hello"],
                "EnvironmentVariables": {"SECRET_TOKEN": "do-not-leak"},
            }
        )
    )

    settings = Settings(
        hermes_ui_launchd_label="test.agent",
        hermes_ui_plist_path=str(plist_path),
        hermes_gateway_plist_path=str(plist_path),
        hermes_launchd_label="test.agent",
    )

    monkeypatch.setattr(
        "backend.operations._launchctl_status",
        lambda _label: {"available": True, "matched": True, "pid": 42},
    )
    monkeypatch.setattr(
        "backend.operations._launchctl_print_state",
        lambda _label: {"available": True, "domain": "gui/501/test.agent", "state": "running"},
    )

    payload = get_operations_status(settings)
    ui_plist = payload["launch_agents"][0]["plist"]
    assert ui_plist["readable"] is True
    assert ui_plist["environment_variable_keys"] == ["SECRET_TOKEN"]
    assert "do-not-leak" not in str(payload)
