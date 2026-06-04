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
    InvalidTaskAssigneeConfig,
    InvalidTaskId,
    InvalidTaskInput,
    TaskNotFound,
    build_task_create_response,
    build_task_list_response,
    build_task_show_response,
    clamp_list_limit,
    create_kanban_argv,
    list_kanban_argv,
    normalize_task_input,
    reset_task_cooldown,
    run_create_kanban_task,
    run_list_kanban_tasks,
    run_show_kanban_task,
    show_kanban_argv,
    validate_task_assignee,
    validate_task_id,
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


def test_create_argv_includes_server_controlled_assignee() -> None:
    settings = Settings(allow_bob_tasks=True, bob_task_assignee="default")
    argv = create_kanban_argv(
        settings,
        title="T",
        body=None,
        idempotency_key="key-1",
    )

    assert "--assignee" in argv
    assert argv[argv.index("--assignee") + 1] == "default"
    assert argv[-3:] == ["--idempotency-key", "key-1", "--json"]


def test_validate_task_assignee_rejects_unsafe_config() -> None:
    assert validate_task_assignee("") is None
    assert validate_task_assignee("default.worker-1") == "default.worker-1"
    with pytest.raises(InvalidTaskAssigneeConfig):
        validate_task_assignee("default;rm")
    with pytest.raises(InvalidTaskAssigneeConfig):
        validate_task_assignee("default worker")


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


def test_api_bob_tasks_uses_server_assignee_and_ignores_client_assignee(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setenv("ALLOW_BOB_TASKS", "true")
    monkeypatch.setenv("HERMES_BOB_TASK_ASSIGNEE", "default")
    monkeypatch.setenv("HERMES_UI_BOB_AUDIT_LOG", str(tmp_path / "bob.log"))
    captured: dict[str, list[str]] = {}

    def fake_runner(args: list[str], timeout: float) -> subprocess.CompletedProcess[str]:
        captured["args"] = args
        return subprocess.CompletedProcess(
            args=args,
            returncode=0,
            stdout=_success_stdout("t_ui_assignee", "ready"),
            stderr="",
        )

    monkeypatch.setattr("backend.bob_tasks._default_runner", fake_runner)
    client = TestClient(app)

    response = client.post(
        "/api/bob/tasks",
        json={"title": "UI test", "body": "From pytest", "assignee": "bob"},
    )

    assert response.status_code == 202
    payload = response.json()
    assert payload["assignee"] == "default"
    assert captured["args"].count("--assignee") == 1
    assert captured["args"][captured["args"].index("--assignee") + 1] == "default"
    assert "bob" not in captured["args"]


def test_api_bob_tasks_rejects_invalid_server_assignee(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ALLOW_BOB_TASKS", "true")
    monkeypatch.setenv("HERMES_BOB_TASK_ASSIGNEE", "bad value")
    client = TestClient(app)

    response = client.post(
        "/api/bob/tasks",
        json={"title": "UI test", "body": "From pytest"},
    )

    assert response.status_code == 500
    assert response.json()["detail"]["error"] == "invalid_bob_task_assignee_config"


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


def _list_stdout(tasks: list[dict] | None = None) -> str:
    items = tasks or [
        {
            "id": "t_79f256ed",
            "title": "UI task",
            "status": "ready",
            "created_at": 1780560000,
        },
        {
            "id": "t_older",
            "title": "Older",
            "status": "done",
            "created_at": 1780550000,
        },
    ]
    return json.dumps(items)


def _show_stdout(task_id: str = "t_79f256ed") -> str:
    return json.dumps(
        {
            "task": {
                "id": task_id,
                "title": "UI task",
                "body": "Do something",
                "status": "done",
                "result": "Completed OK",
                "created_at": 1780560000,
            },
            "events": [{"kind": "created", "created_at": 1780560000}],
            "comments": [{"text": "Done", "created_at": 1780560100}],
            "latest_summary": None,
        }
    )


def test_validate_task_id_accepts_and_rejects() -> None:
    assert validate_task_id("t_79f256ed") == "t_79f256ed"
    with pytest.raises(InvalidTaskId):
        validate_task_id("bad id")
    with pytest.raises(InvalidTaskId):
        validate_task_id("no-prefix")
    with pytest.raises(InvalidTaskId):
        validate_task_id("t_../escape")


def test_clamp_list_limit() -> None:
    assert clamp_list_limit(None) == 20
    assert clamp_list_limit(5) == 5
    assert clamp_list_limit(100) == 50


def test_list_argv_is_fixed() -> None:
    settings = Settings(allow_bob_tasks=True)
    argv = list_kanban_argv(settings)
    assert argv == [
        settings.hermes_cli_bin,
        "kanban",
        "list",
        "--json",
    ]
    assert "chat" not in argv
    assert "-z" not in argv


def test_show_argv_is_fixed() -> None:
    settings = Settings(allow_bob_tasks=True)
    argv = show_kanban_argv(settings, "t_abc")
    assert argv == [
        settings.hermes_cli_bin,
        "kanban",
        "show",
        "t_abc",
        "--json",
    ]


def test_list_respects_limit_slice() -> None:
    settings = Settings(allow_bob_tasks=True)
    tasks = [{"id": f"t_{i}", "title": str(i), "status": "ready"} for i in range(30)]

    def fake_runner(args: list[str], timeout: float) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(
            args=args,
            returncode=0,
            stdout=_list_stdout(tasks),
            stderr="",
        )

    payload = build_task_list_response(settings, limit=10, runner=fake_runner)
    assert payload["success"] is True
    assert payload["count"] == 10
    assert len(payload["tasks"]) == 10


def test_show_no_such_task_returns_404_via_api(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ALLOW_BOB_TASKS", "true")

    def fake_runner(args: list[str], timeout: float) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(
            args=args,
            returncode=0,
            stdout="",
            stderr="no such task: t_missing",
        )

    monkeypatch.setattr("backend.bob_tasks._default_runner", fake_runner)
    client = TestClient(app)
    response = client.get("/api/bob/tasks/t_missing")

    assert response.status_code == 404
    assert response.json()["detail"]["error"] == "task_not_found"


def test_api_list_tasks_returns_403_when_disabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ALLOW_BOB_TASKS", "false")
    client = TestClient(app)
    response = client.get("/api/bob/tasks")
    assert response.status_code == 403


def test_api_list_tasks_returns_200_when_enabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ALLOW_BOB_TASKS", "true")

    def fake_runner(args: list[str], timeout: float) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(
            args=args,
            returncode=0,
            stdout=_list_stdout(),
            stderr="",
        )

    monkeypatch.setattr("backend.bob_tasks._default_runner", fake_runner)
    client = TestClient(app)
    response = client.get("/api/bob/tasks?limit=5")

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert len(payload["tasks"]) == 2
    assert payload["limit"] == 5


def test_api_show_task_returns_400_for_invalid_id(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ALLOW_BOB_TASKS", "true")
    client = TestClient(app)
    response = client.get("/api/bob/tasks/not-valid")
    assert response.status_code == 400


def test_api_show_task_returns_200_when_enabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ALLOW_BOB_TASKS", "true")

    def fake_runner(args: list[str], timeout: float) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(
            args=args,
            returncode=0,
            stdout=_show_stdout("t_79f256ed"),
            stderr="",
        )

    monkeypatch.setattr("backend.bob_tasks._default_runner", fake_runner)
    client = TestClient(app)
    response = client.get("/api/bob/tasks/t_79f256ed")

    assert response.status_code == 200
    payload = response.json()
    assert payload["task_id"] == "t_79f256ed"
    assert payload["task"]["status"] == "done"
    assert payload["events"]


def test_api_list_tasks_returns_502_on_cli_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ALLOW_BOB_TASKS", "true")

    def fake_runner(args: list[str], timeout: float) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(
            args=args,
            returncode=1,
            stdout="",
            stderr="failed",
        )

    monkeypatch.setattr("backend.bob_tasks._default_runner", fake_runner)
    client = TestClient(app)
    response = client.get("/api/bob/tasks")
    assert response.status_code == 502


def test_api_list_tasks_returns_502_on_json_parse_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ALLOW_BOB_TASKS", "true")

    def fake_runner(args: list[str], timeout: float) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(
            args=args,
            returncode=0,
            stdout="not-json",
            stderr="",
        )

    monkeypatch.setattr("backend.bob_tasks._default_runner", fake_runner)
    client = TestClient(app)
    response = client.get("/api/bob/tasks")
    assert response.status_code == 502


def test_run_list_requires_feature_gate() -> None:
    with pytest.raises(BobTasksDisabled):
        run_list_kanban_tasks(Settings(allow_bob_tasks=False))


def test_build_show_raises_task_not_found() -> None:
    settings = Settings(allow_bob_tasks=True)

    def fake_runner(args: list[str], timeout: float) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(
            args=args,
            returncode=0,
            stdout="no such task: t_abc",
            stderr="",
        )

    with pytest.raises(TaskNotFound):
        build_task_show_response(settings, "t_abc", runner=fake_runner)
