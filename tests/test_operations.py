"""Tests for read-only operations status."""

from __future__ import annotations

import plistlib
from pathlib import Path

from fastapi.testclient import TestClient

from backend.config import Settings
from backend.main import app
from backend.operations import get_operations_status
from backend.status import CommandResult

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
    assert "cloudflare_tunnel" in payload
    assert payload["cloudflare_tunnel"]["observation_scope"] == "local_agent_and_edge_probe"
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


def _mock_launch_agents(monkeypatch) -> None:
    monkeypatch.setattr(
        "backend.operations._launchctl_status",
        lambda _label: {"available": True, "matched": True, "pid": 42},
    )
    monkeypatch.setattr(
        "backend.operations._launchctl_print_state",
        lambda _label: {
            "available": True,
            "domain": "gui/501/test.agent",
            "state": "running",
        },
    )


def test_cloudflare_tunnel_edge_probe_302(monkeypatch, tmp_path: Path) -> None:
    plist_path = tmp_path / "agent.plist"
    plist_path.write_bytes(plistlib.dumps({"Label": "test.agent", "ProgramArguments": ["/bin/true"]}))
    settings = Settings(
        hermes_ui_plist_path=str(plist_path),
        hermes_gateway_plist_path=str(plist_path),
        hermes_ui_launchd_label="test.agent",
        hermes_launchd_label="test.agent",
        hermes_ops_edge_probe=True,
    )
    _mock_launch_agents(monkeypatch)

    def fake_run(args: list[str], timeout: float = 2.0) -> CommandResult:
        if args[:3] == ["/usr/bin/curl", "-sS", "-D"]:
            return CommandResult(
                ok=True,
                stdout=(
                    "HTTP/2 302 \r\n"
                    "location: https://truls.cloudflareaccess.com/cdn-cgi/access/login\r\n"
                ),
                stderr="",
            )
        if args == ["/usr/bin/which", "cloudflared"]:
            return CommandResult(ok=True, stdout="/opt/homebrew/bin/cloudflared", stderr="")
        if len(args) >= 2 and args[1] == "--version":
            return CommandResult(ok=True, stdout="cloudflared version 2026.5.1", stderr="")
        if args[:3] == ["/usr/bin/pgrep", "-lf", "cloudflared"]:
            return CommandResult(ok=True, stdout="123 cloudflared tunnel run", stderr="")
        return CommandResult(ok=False, stdout="", stderr="unexpected")

    monkeypatch.setattr("backend.operations._run_read_only", fake_run)
    payload = get_operations_status(settings)
    tunnel = payload["cloudflare_tunnel"]
    assert tunnel["edge_probe"]["http_status"] == 302
    assert tunnel["edge_probe"]["access_redirect"] is True
    assert tunnel["cloudflared"]["process_running"] is True
    assert "cloudflareaccess.com" in (tunnel["edge_probe"]["location_host"] or "")


def test_cloudflare_tunnel_edge_probe_disabled(monkeypatch, tmp_path: Path) -> None:
    plist_path = tmp_path / "agent.plist"
    plist_path.write_bytes(plistlib.dumps({"Label": "test.agent", "ProgramArguments": ["/bin/true"]}))
    settings = Settings(
        hermes_ui_plist_path=str(plist_path),
        hermes_gateway_plist_path=str(plist_path),
        hermes_ui_launchd_label="test.agent",
        hermes_launchd_label="test.agent",
        hermes_ops_edge_probe=False,
    )
    _mock_launch_agents(monkeypatch)
    payload = get_operations_status(settings)
    assert payload["cloudflare_tunnel"]["edge_probe"]["enabled"] is False
    assert payload["cloudflare_tunnel"]["edge_probe"]["attempted"] is False


def test_cloudflare_tunnel_redacts_cloudflared_paths(monkeypatch, tmp_path: Path) -> None:
    plist_path = tmp_path / "agent.plist"
    plist_path.write_bytes(plistlib.dumps({"Label": "test.agent", "ProgramArguments": ["/bin/true"]}))
    settings = Settings(
        hermes_ui_plist_path=str(plist_path),
        hermes_gateway_plist_path=str(plist_path),
        hermes_ui_launchd_label="test.agent",
        hermes_launchd_label="test.agent",
        hermes_ops_edge_probe=False,
    )
    _mock_launch_agents(monkeypatch)

    def fake_run(args: list[str], timeout: float = 2.0) -> CommandResult:
        if args[:3] == ["/usr/bin/pgrep", "-lf", "cloudflared"]:
            return CommandResult(
                ok=True,
                stdout="99 cloudflared --config /Users/x/.cloudflared/secret.json tunnel run",
                stderr="",
            )
        if args == ["/usr/bin/which", "cloudflared"]:
            return CommandResult(ok=True, stdout="/opt/homebrew/bin/cloudflared", stderr="")
        if len(args) >= 2 and args[1] == "--version":
            return CommandResult(ok=True, stdout="cloudflared version 1.0", stderr="")
        return CommandResult(ok=False, stdout="", stderr="")

    monkeypatch.setattr("backend.operations._run_read_only", fake_run)
    payload = get_operations_status(settings)
    summary = payload["cloudflare_tunnel"]["cloudflared"]["process_summary"]
    assert summary is not None
    assert "secret.json" not in summary
    assert ".cloudflared/[redacted]" in summary
    assert "secret" not in str(payload)
