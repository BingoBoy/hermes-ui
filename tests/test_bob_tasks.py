"""Tests for allowlisted Bob kanban task creation."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.bob_tasks import (
    CREATE_KANBAN_TASK_ACTION,
    BobTasksDisabled,
    CooldownActive,
    InvalidTaskInput,
    build_task_create_response,
    create_kanban_argv,
    normalize_task_input,
    reset_task_cooldown,
    run_create_kanban_task,
    write_audit_entry,
)
from backend.config import Settings
from backend.main import app


@pytest.fixture(autouse=True)
def _reset_cooldown() -> None:
    reset_task_cooldown()


def _success_stdout(task_id: str = "t_abc123", status: str = "ready") -> str:
    return json.dumps({"id": task_id, "status": status, "title": "Test"})


def test_normalize_rejects_empty_and_newline_title() -> None:
    with pytest.raises(InvalidTaskInput):
        normalize_task_input("", None)
    with pytest.raises(InvalidTaskInput):
        normalize_task_input("   ", None)
    with pytest.raises(InvalidTaskInput):
        normalize_task_input("line\nbreak", None)


def test_normalize_rejects_long_fields() -> None:
    with pytest.raises(InvalidTaskInput):
        normalize_task_input("x" * 201, None)
    with pytest.raises(InvalidTaskInput):
        normalize_task_input("ok", "y" * 4001)


def test_create_argv_fixed_and_omits_empty_body() -> None:
    settings = Settings(allow_bob_tasks=True)
    argv = create_kanban_argv(
        settings,
        title="Task title",
        body=None,
        idempotency_key="550e8400-e29b-41d4-a716-446655440000",
    )

    assert argv[0] == settings.hermes_cli_bin
    assert argv[1:4] == ["kanban", "create", "Task title"]
    assert "--body" not in argv
    assert argv[-3:] == [
        "--idempotency-key",
        "550e8400-e29b-41d4-a716-446655440000",
        "--json",
    ]
    assert "-z" not in argv
    assert "chat" not in argv


def test_create_argv_includes_body_when_present() -> None:
    settings = Settings(allow_bob_tasks=True)
    argv = create_kanban_argv(
        settings,
        title="T",
        body="Body text",
        idempotency_key="key-1",
    )

    assert argv[4:6] == ["--body", "Body text"]


def test_run_create_requires_feature_gate() -> None:
    settings = Settings(allow_bob_tasks=False)

    with pytest.raises(BobTasksDisabled):
        run_create_kanban_task(settings, title="T", body=None)


def test_run_create_uses_subprocess_without_shell(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    settings = Settings(allow_bob_tasks=True)
    captured: dict[str, object] = {}

    def fake_runner(args: list[str], timeout: float) -> subprocess.CompletedProcess[str]:
        captured["args"] = args
        captured["timeout"] = timeout
        return subprocess.CompletedProcess(
            args=args,
            returncode=0,
            stdout=_success_stdout(),
            stderr="",
        )

    result = run_create_kanban_task(
        settings, title="Hello", body="World", runner=fake_runner
    )

    assert result.ok is True
    assert result.task_id == "t_abc123"
    assert result.status == "ready"
    assert captured["timeout"] == 30.0
    argv = captured["args"]
    assert isinstance(argv, list)
    assert argv[1:4] == ["kanban", "create", "Hello"]
    assert "--json" in argv


def test_default_runner_never_uses_shell_true() -> None:
    source = Path("backend/bob_tasks.py").read_text(encoding="utf-8")
    assert "shell=True" not in source
    assert "shell = True" not in source


def test_write_audit_entry_does_not_log_body(tmp_path: Path) -> None:
    settings = Settings(allow_bob_tasks=True)
    audit_path = tmp_path / "bob.log"

    write_audit_entry(
        settings,
        audit_id="audit-1",
        action=CREATE_KANBAN_TASK_ACTION,
        success=True,
        exit_code=0,
        detail=None,
        title_hash="sha256:abc",
        body_length=12,
        task_id="t_1",
        audit_path=audit_path,
    )

    payload = json.loads(audit_path.read_text(encoding="utf-8").strip())
    assert payload["title_hash"] == "sha256:abc"
    assert payload["body_length"] == 12
    assert "body" not in payload


def test_cli_failure_returns_not_ok() -> None:
    settings = Settings(allow_bob_tasks=True)

    def fake_runner(args: list[str], timeout: float) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(
            args=args,
            returncode=2,
            stdout="",
            stderr="missing title",
        )

    result = run_create_kanban_task(
        settings, title="T", body=None, runner=fake_runner
    )

    assert result.ok is False
    assert result.exit_code == 2


def test_invalid_json_stdout_returns_not_ok() -> None:
    settings = Settings(allow_bob_tasks=True)

    def fake_runner(args: list[str], timeout: float) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(
            args=args,
            returncode=0,
            stdout="not json",
            stderr="",
        )

    result = run_create_kanban_task(
        settings, title="T", body=None, runner=fake_runner
    )

    assert result.ok is False


def test_cooldown_blocks_second_create(tmp_path: Path) -> None:
    settings = Settings(allow_bob_tasks=True)
    audit_path = tmp_path / "audit.log"

    def fake_runner(args: list[str], timeout: float) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(
            args=args,
            returncode=0,
            stdout=_success_stdout(),
            stderr="",
        )

    now = 1000.0
    build_task_create_response(
        settings,
        title="First",
        body=None,
        runner=fake_runner,
        audit_path=audit_path,
        now=now,
    )

    with pytest.raises(CooldownActive) as exc_info:
        build_task_create_response(
            settings,
            title="Second",
            body=None,
            runner=fake_runner,
            audit_path=audit_path,
            now=now + 5,
        )

    assert exc_info.value.retry_after > 0


def test_api_bob_tasks_returns_403_when_disabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ALLOW_BOB_TASKS", "false")
    client = TestClient(app)

    response = client.post(
        "/api/bob/tasks",
        json={"title": "Test", "body": "Body"},
    )

    assert response.status_code == 403
    detail = response.json()["detail"]
    assert detail["error"] == "bob_tasks_disabled"


def test_api_bob_tasks_returns_202_when_enabled(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setenv("ALLOW_BOB_TASKS", "true")
    monkeypatch.setenv("HERMES_UI_BOB_AUDIT_LOG", str(tmp_path / "bob.log"))

    def fake_runner(args: list[str], timeout: float) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(
            args=args,
            returncode=0,
            stdout=_success_stdout("t_ui_test", "ready"),
            stderr="",
        )

    monkeypatch.setattr("backend.bob_tasks._default_runner", fake_runner)
    client = TestClient(app)

    response = client.post(
        "/api/bob/tasks",
        json={"title": "UI test", "body": "From pytest"},
    )

    assert response.status_code == 202
    payload = response.json()
    assert payload["success"] is True
    assert payload["task_id"] == "t_ui_test"
    assert payload["status"] == "ready"
    assert "audit_id" in payload


def test_api_bob_tasks_returns_400_for_invalid_title(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ALLOW_BOB_TASKS", "true")
    client = TestClient(app)

    response = client.post(
        "/api/bob/tasks",
        json={"title": "bad\nline", "body": ""},
    )

    assert response.status_code == 400
    assert response.json()["detail"]["error"] == "invalid_input"


def test_api_bob_tasks_returns_400_for_long_title(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ALLOW_BOB_TASKS", "true")
    client = TestClient(app)

    response = client.post(
        "/api/bob/tasks",
        json={"title": "x" * 201, "body": ""},
    )

    assert response.status_code == 400


def test_api_bob_tasks_returns_400_for_long_body(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ALLOW_BOB_TASKS", "true")
    client = TestClient(app)

    response = client.post(
        "/api/bob/tasks",
        json={"title": "ok", "body": "y" * 4001},
    )

    assert response.status_code == 400


def test_api_bob_tasks_returns_429_on_cooldown(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setenv("ALLOW_BOB_TASKS", "true")
    monkeypatch.setenv("HERMES_UI_BOB_AUDIT_LOG", str(tmp_path / "bob.log"))

    def fake_runner(args: list[str], timeout: float) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(
            args=args,
            returncode=0,
            stdout=_success_stdout(),
            stderr="",
        )

    monkeypatch.setattr("backend.bob_tasks._default_runner", fake_runner)
    client = TestClient(app)
    first = client.post("/api/bob/tasks", json={"title": "One", "body": ""})
    second = client.post("/api/bob/tasks", json={"title": "Two", "body": ""})

    assert first.status_code == 202
    assert second.status_code == 429
    assert second.json()["detail"]["error"] == "cooldown_active"


def test_api_bob_tasks_returns_502_on_cli_failure(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setenv("ALLOW_BOB_TASKS", "true")
    monkeypatch.setenv("HERMES_UI_BOB_AUDIT_LOG", str(tmp_path / "bob.log"))

    def fake_runner(args: list[str], timeout: float) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(
            args=args,
            returncode=2,
            stdout="",
            stderr="cli failed",
        )

    monkeypatch.setattr("backend.bob_tasks._default_runner", fake_runner)
    client = TestClient(app)

    response = client.post(
        "/api/bob/tasks",
        json={"title": "Fail", "body": ""},
    )

    assert response.status_code == 502


def test_api_bob_tasks_returns_502_on_json_parse_failure(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setenv("ALLOW_BOB_TASKS", "true")
    monkeypatch.setenv("HERMES_UI_BOB_AUDIT_LOG", str(tmp_path / "bob.log"))

    def fake_runner(args: list[str], timeout: float) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(
            args=args,
            returncode=0,
            stdout="<<<not json>>>",
            stderr="",
        )

    monkeypatch.setattr("backend.bob_tasks._default_runner", fake_runner)
    client = TestClient(app)

    response = client.post(
        "/api/bob/tasks",
        json={"title": "Parse fail", "body": ""},
    )

    assert response.status_code == 502


def test_bob_tasks_code_does_not_target_hermes_ui_label() -> None:
    source = Path("backend/bob_tasks.py").read_text(encoding="utf-8")
    assert "no.truls.hermes-ui" not in source
