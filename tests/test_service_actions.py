"""Tests for allowlisted Hermes Gateway service actions."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.config import Settings
from backend.main import app
from backend.service_actions import (
    ALLOWED_GATEWAY_LABEL,
    RESTART_ACTION,
    ActionNotAllowed,
    CooldownActive,
    ServiceActionsDisabled,
    build_restart_response,
    reset_restart_cooldown,
    restart_argv,
    run_allowlisted_action,
    write_audit_entry,
)


@pytest.fixture(autouse=True)
def _reset_cooldown() -> None:
    reset_restart_cooldown()


def test_restart_argv_is_fixed_and_targets_gateway_only() -> None:
    settings = Settings(allow_service_actions=True, hermes_launchd_label=ALLOWED_GATEWAY_LABEL)
    argv = restart_argv(settings)

    assert argv[0] == "launchctl"
    assert argv[1:4] == ["kickstart", "-k", f"gui/{__import__('os').getuid()}/{ALLOWED_GATEWAY_LABEL}"]
    assert "no.truls.hermes-ui" not in " ".join(argv)


def test_restart_argv_rejects_non_gateway_label() -> None:
    settings = Settings(allow_service_actions=True, hermes_launchd_label="no.truls.hermes-ui")

    with pytest.raises(ActionNotAllowed):
        restart_argv(settings)


def test_run_allowlisted_action_rejects_unknown_action() -> None:
    settings = Settings(allow_service_actions=True)

    with pytest.raises(ActionNotAllowed):
        run_allowlisted_action("start_hermes_gateway", settings)


def test_run_allowlisted_action_requires_feature_gate() -> None:
    settings = Settings(allow_service_actions=False)

    with pytest.raises(ServiceActionsDisabled):
        run_allowlisted_action(RESTART_ACTION, settings)


def test_run_allowlisted_action_uses_subprocess_without_shell(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    settings = Settings(allow_service_actions=True, hermes_launchd_label=ALLOWED_GATEWAY_LABEL)
    captured: dict[str, object] = {}

    def fake_runner(args: list[str], timeout: float) -> subprocess.CompletedProcess[str]:
        captured["args"] = args
        captured["timeout"] = timeout
        return subprocess.CompletedProcess(args=args, returncode=0, stdout="", stderr="")

    result = run_allowlisted_action(RESTART_ACTION, settings, runner=fake_runner)

    assert result.ok is True
    assert captured["args"] == restart_argv(settings)
    assert captured["timeout"] == 5.0


def test_default_runner_never_uses_shell_true() -> None:
    source = Path("backend/service_actions.py").read_text(encoding="utf-8")
    assert "shell=True" not in source
    assert "shell = True" not in source


def test_write_audit_entry_appends_jsonl(tmp_path: Path) -> None:
    settings = Settings(allow_service_actions=True)
    audit_path = tmp_path / "service-actions.log"

    write_audit_entry(
        settings,
        audit_id="test-audit",
        action=RESTART_ACTION,
        success=True,
        exit_code=0,
        detail=None,
        audit_path=audit_path,
    )

    line = audit_path.read_text(encoding="utf-8").strip()
    payload = json.loads(line)
    assert payload["audit_id"] == "test-audit"
    assert payload["action"] == RESTART_ACTION
    assert payload["target_label"] == ALLOWED_GATEWAY_LABEL
    assert payload["success"] is True


def test_build_restart_response_writes_audit_and_refreshes_status(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    settings = Settings(allow_service_actions=True, hermes_launchd_label=ALLOWED_GATEWAY_LABEL)
    audit_path = tmp_path / "audit.log"

    def fake_runner(args: list[str], timeout: float) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(args=args, returncode=0, stdout="", stderr="")

    monkeypatch.setattr(
        "backend.service_actions.get_hermes_status",
        lambda _settings: {"running": True, "state": "running"},
    )

    payload = build_restart_response(settings, runner=fake_runner, audit_path=audit_path)

    assert payload["success"] is True
    assert payload["action"] == "restart"
    assert payload["hermes_status"]["running"] is True
    assert audit_path.read_text(encoding="utf-8").strip()


def test_cooldown_blocks_second_restart(tmp_path: Path) -> None:
    settings = Settings(allow_service_actions=True, hermes_launchd_label=ALLOWED_GATEWAY_LABEL)
    audit_path = tmp_path / "audit.log"

    def fake_runner(args: list[str], timeout: float) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(args=args, returncode=0, stdout="", stderr="")

    now = 1000.0
    build_restart_response(settings, runner=fake_runner, audit_path=audit_path, now=now)

    with pytest.raises(CooldownActive) as exc_info:
        build_restart_response(
            settings,
            runner=fake_runner,
            audit_path=audit_path,
            now=now + 5,
        )

    assert exc_info.value.retry_after > 0


def test_api_restart_returns_403_when_disabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ALLOW_SERVICE_ACTIONS", "false")
    client = TestClient(app)

    response = client.post("/api/hermes/restart")

    assert response.status_code == 403
    detail = response.json()["detail"]
    assert detail["error"] == "service_actions_disabled"


def test_api_restart_returns_structured_success_when_enabled(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setenv("ALLOW_SERVICE_ACTIONS", "true")
    monkeypatch.setenv("HERMES_UI_AUDIT_LOG", str(tmp_path / "audit.log"))

    def fake_runner(args: list[str], timeout: float) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(args=args, returncode=0, stdout="", stderr="")

    monkeypatch.setattr("backend.service_actions._default_runner", fake_runner)
    monkeypatch.setattr(
        "backend.service_actions.get_hermes_status",
        lambda _settings: {"running": True, "state": "running"},
    )

    client = TestClient(app)
    response = client.post("/api/hermes/restart")

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["action"] == "restart"
    assert payload["launchd_label"] == ALLOWED_GATEWAY_LABEL
    assert "audit_id" in payload
    assert "hermes_status" in payload


def test_api_restart_returns_429_on_cooldown(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setenv("ALLOW_SERVICE_ACTIONS", "true")
    monkeypatch.setenv("HERMES_UI_AUDIT_LOG", str(tmp_path / "audit.log"))

    def fake_runner(args: list[str], timeout: float) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(args=args, returncode=0, stdout="", stderr="")

    monkeypatch.setattr("backend.service_actions._default_runner", fake_runner)
    monkeypatch.setattr(
        "backend.service_actions.get_hermes_status",
        lambda _settings: {"running": True, "state": "running"},
    )

    client = TestClient(app)
    first = client.post("/api/hermes/restart")
    second = client.post("/api/hermes/restart")

    assert first.status_code == 200
    assert second.status_code == 429
    detail = second.json()["detail"]
    assert detail["error"] == "cooldown_active"


def test_service_action_code_does_not_target_hermes_ui_label() -> None:
    source = Path("backend/service_actions.py").read_text(encoding="utf-8")
    assert "no.truls.hermes-ui" not in source
