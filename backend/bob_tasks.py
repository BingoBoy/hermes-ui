"""Allowlisted Bob kanban task create and read-only list/show via Hermes CLI."""

from __future__ import annotations

import hashlib
import json
import os
import re
import secrets
import subprocess
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from backend.config import Settings
from backend.redaction import redact_line

CREATE_KANBAN_TASK_ACTION = "create_kanban_task"
LIST_KANBAN_TASKS_ACTION = "list_kanban_tasks"
SHOW_KANBAN_TASK_ACTION = "show_kanban_task"
ALLOWED_WRITE_ACTIONS = frozenset({CREATE_KANBAN_TASK_ACTION})
ALLOWED_READ_ACTIONS = frozenset({LIST_KANBAN_TASKS_ACTION, SHOW_KANBAN_TASK_ACTION})

DEFAULT_LIST_LIMIT = 20
MAX_LIST_LIMIT = 50
MAX_TASK_ID_LENGTH = 80
_TASK_ID_PATTERN = re.compile(r"^t_[a-zA-Z0-9_-]+$")
_ASSIGNEE_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+$")

DEFAULT_HERMES_CLI_BIN = "/Users/trulsdahl/.hermes/hermes-agent/venv/bin/hermes"
DEFAULT_AUDIT_LOG = "/Users/trulsdahl/.hermes-ui/logs/bob-interactions.log"

MAX_TITLE_LENGTH = 200
MAX_BODY_LENGTH = 4000
ACTION_TIMEOUT_SECONDS = 30.0
COOLDOWN_SECONDS = 60
MAX_DETAIL_LENGTH = 200

CommandRunner = Callable[[list[str], float], subprocess.CompletedProcess[str]]

_last_task_create_at: float | None = None


class BobTasksDisabled(Exception):
    """Raised when ALLOW_BOB_TASKS is false."""


class ActionNotAllowed(Exception):
    """Raised when an action is not in the allowlist."""


class InvalidTaskInput(Exception):
    """Raised when title/body fail validation."""


class InvalidTaskAssigneeConfig(Exception):
    """Raised when server-side Bob task assignee config is invalid."""


class InvalidTaskId(Exception):
    """Raised when task_id fails validation."""


class TaskNotFound(Exception):
    """Raised when kanban show reports a missing task."""


class CooldownActive(Exception):
    """Raised when task creation was requested too recently."""

    def __init__(self, retry_after: int) -> None:
        self.retry_after = retry_after
        super().__init__(f"Cooldown active; retry in {retry_after} seconds")


@dataclass(frozen=True)
class TaskCreateResult:
    ok: bool
    exit_code: int
    stdout: str
    stderr: str
    task_id: str | None = None
    status: str | None = None
    detail: str | None = None


@dataclass(frozen=True)
class KanbanReadResult:
    ok: bool
    exit_code: int
    stdout: str
    stderr: str
    detail: str | None = None
    not_found: bool = False


def _default_runner(args: list[str], timeout: float) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        check=False,
        capture_output=True,
        text=True,
        timeout=timeout,
        shell=False,
    )


def _audit_log_path(settings: Settings) -> Path:
    raw = os.getenv("HERMES_UI_BOB_AUDIT_LOG", DEFAULT_AUDIT_LOG).strip()
    return Path(raw or DEFAULT_AUDIT_LOG)


def _sanitize_detail(text: str, *, max_length: int = MAX_DETAIL_LENGTH) -> str:
    redacted, _ = redact_line(text.strip(), in_private_key_block=False)
    if len(redacted) > max_length:
        return redacted[: max_length - 3] + "..."
    return redacted


def _make_audit_id(action: str) -> str:
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return f"{timestamp}-{action}-{secrets.token_hex(4)}"


def _title_hash(title: str) -> str:
    digest = hashlib.sha256(title.encode("utf-8")).hexdigest()
    return f"sha256:{digest}"


def normalize_task_input(title: str, body: str | None) -> tuple[str, str | None]:
    """Validate and normalize title/body from API input."""
    if title is None:
        raise InvalidTaskInput("title is required")

    normalized_title = title.strip()
    if not normalized_title:
        raise InvalidTaskInput("title is required")
    if "\n" in normalized_title or "\r" in normalized_title:
        raise InvalidTaskInput("title must not contain newlines")
    if len(normalized_title) > MAX_TITLE_LENGTH:
        raise InvalidTaskInput(f"title must be at most {MAX_TITLE_LENGTH} characters")

    normalized_body: str | None = None
    if body is not None:
        stripped = body.strip()
        if stripped:
            if len(stripped) > MAX_BODY_LENGTH:
                raise InvalidTaskInput(
                    f"body must be at most {MAX_BODY_LENGTH} characters"
                )
            normalized_body = stripped

    return normalized_title, normalized_body


def validate_task_assignee(assignee: str | None) -> str | None:
    """Validate optional server-controlled kanban assignee profile."""
    if assignee is None:
        return None

    normalized = assignee.strip()
    if not normalized:
        return None
    if len(normalized) > 80:
        raise InvalidTaskAssigneeConfig("HERMES_BOB_TASK_ASSIGNEE is too long")
    if not _ASSIGNEE_PATTERN.match(normalized):
        raise InvalidTaskAssigneeConfig(
            "HERMES_BOB_TASK_ASSIGNEE contains invalid characters"
        )
    return normalized


def create_kanban_argv(
    settings: Settings,
    *,
    title: str,
    body: str | None,
    idempotency_key: str,
) -> list[str]:
    """Return fixed argv for hermes kanban create."""
    argv = [
        settings.hermes_cli_bin,
        "kanban",
        "create",
        title,
    ]
    if body:
        argv.extend(["--body", body])
    assignee = validate_task_assignee(settings.bob_task_assignee)
    if assignee:
        argv.extend(["--assignee", assignee])
    argv.extend(["--idempotency-key", idempotency_key, "--json"])
    return argv


def write_audit_entry(
    settings: Settings,
    *,
    audit_id: str,
    action: str,
    success: bool,
    exit_code: int | None,
    detail: str | None,
    title_hash: str | None = None,
    body_length: int | None = None,
    task_id: str | None = None,
    audit_path: Path | None = None,
) -> None:
    """Append one JSONL audit record for Bob interactions."""
    path = audit_path or _audit_log_path(settings)
    path.parent.mkdir(parents=True, exist_ok=True)
    entry: dict[str, Any] = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "audit_id": audit_id,
        "action": action,
        "actor": "hermes-ui",
        "auth_layer": "cloudflare-access",
        "success": success,
        "exit_code": exit_code,
        "detail": detail,
    }
    if title_hash is not None:
        entry["title_hash"] = title_hash
    if body_length is not None:
        entry["body_length"] = body_length
    if task_id is not None:
        entry["task_id"] = task_id
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=True) + "\n")


def reset_task_cooldown() -> None:
    """Reset cooldown state — intended for tests."""
    global _last_task_create_at
    _last_task_create_at = None


def _check_cooldown(now: float | None = None) -> None:
    global _last_task_create_at
    current = now if now is not None else time.monotonic()
    if _last_task_create_at is None:
        return
    elapsed = current - _last_task_create_at
    if elapsed < COOLDOWN_SECONDS:
        retry_after = max(1, int(COOLDOWN_SECONDS - elapsed))
        raise CooldownActive(retry_after)


def _mark_task_created(now: float | None = None) -> None:
    global _last_task_create_at
    _last_task_create_at = now if now is not None else time.monotonic()


def _parse_create_stdout(stdout: str) -> tuple[str, str]:
    try:
        payload = json.loads(stdout)
    except json.JSONDecodeError as exc:
        raise ValueError("invalid kanban JSON output") from exc
    if not isinstance(payload, dict):
        raise ValueError("kanban output must be a JSON object")
    task_id = payload.get("id")
    status = payload.get("status")
    if not task_id or not isinstance(task_id, str):
        raise ValueError("kanban output missing task id")
    if not status or not isinstance(status, str):
        raise ValueError("kanban output missing status")
    return task_id, status


def run_create_kanban_task(
    settings: Settings,
    *,
    title: str,
    body: str | None,
    idempotency_key: str | None = None,
    runner: CommandRunner | None = None,
    now: float | None = None,
) -> TaskCreateResult:
    """Execute create_kanban_task with fixed argv and no shell."""
    if not settings.allow_bob_tasks:
        raise BobTasksDisabled()

    normalized_title, normalized_body = normalize_task_input(title, body)
    key = idempotency_key or str(uuid.uuid4())
    argv = create_kanban_argv(
        settings,
        title=normalized_title,
        body=normalized_body,
        idempotency_key=key,
    )

    _check_cooldown(now)
    execute = runner or _default_runner
    try:
        completed = execute(argv, settings.bob_task_timeout_seconds)
    except FileNotFoundError:
        return TaskCreateResult(
            ok=False,
            exit_code=-1,
            stdout="",
            stderr="hermes CLI not found",
            detail="Hermes CLI unavailable",
        )
    except subprocess.TimeoutExpired:
        return TaskCreateResult(
            ok=False,
            exit_code=-1,
            stdout="",
            stderr="action timed out",
            detail="Task creation timed out",
        )
    except OSError as exc:
        safe_detail = _sanitize_detail(str(exc))
        return TaskCreateResult(
            ok=False,
            exit_code=-1,
            stdout="",
            stderr=safe_detail,
            detail=safe_detail or "Task creation failed",
        )

    stdout = completed.stdout.strip()
    stderr = completed.stderr.strip()
    stderr_detail = _sanitize_detail(stderr) if stderr else None

    if completed.returncode != 0:
        if not stderr_detail:
            stderr_detail = f"hermes kanban create exited with code {completed.returncode}"
        return TaskCreateResult(
            ok=False,
            exit_code=completed.returncode,
            stdout=stdout,
            stderr=stderr,
            detail=stderr_detail,
        )

    try:
        task_id, status = _parse_create_stdout(stdout)
    except ValueError as exc:
        return TaskCreateResult(
            ok=False,
            exit_code=completed.returncode,
            stdout=stdout,
            stderr=stderr,
            detail=_sanitize_detail(str(exc)),
        )

    _mark_task_created(now)
    return TaskCreateResult(
        ok=True,
        exit_code=completed.returncode,
        stdout=stdout,
        stderr=stderr,
        task_id=task_id,
        status=status,
    )


def build_task_create_response(
    settings: Settings,
    *,
    title: str,
    body: str | None,
    runner: CommandRunner | None = None,
    audit_path: Path | None = None,
    now: float | None = None,
) -> dict[str, Any]:
    """Create a kanban task and return structured API payload."""
    if not settings.allow_bob_tasks:
        raise BobTasksDisabled()

    audit_id = _make_audit_id(CREATE_KANBAN_TASK_ACTION)
    submitted_at = datetime.now(timezone.utc).isoformat()

    try:
        normalized_title, normalized_body = normalize_task_input(title, body)
    except InvalidTaskInput:
        raise

    title_digest = _title_hash(normalized_title)
    body_len = len(normalized_body) if normalized_body else 0
    assignee = validate_task_assignee(settings.bob_task_assignee)

    try:
        result = run_create_kanban_task(
            settings,
            title=title,
            body=body,
            runner=runner,
            now=now,
        )
    except CooldownActive as exc:
        write_audit_entry(
            settings,
            audit_id=audit_id,
            action=CREATE_KANBAN_TASK_ACTION,
            success=False,
            exit_code=None,
            detail=f"cooldown_active:{exc.retry_after}s",
            title_hash=title_digest,
            body_length=body_len,
            audit_path=audit_path,
        )
        raise

    write_audit_entry(
        settings,
        audit_id=audit_id,
        action=CREATE_KANBAN_TASK_ACTION,
        success=result.ok,
        exit_code=result.exit_code,
        detail=result.detail,
        title_hash=title_digest,
        body_length=body_len,
        task_id=result.task_id,
        audit_path=audit_path,
    )

    if not result.ok:
        return {
            "success": False,
            "error": "task_create_failed",
            "detail": result.detail or "Task creation failed",
            "audit_id": audit_id,
            "submitted_at": submitted_at,
        }

    return {
        "success": True,
        "task_id": result.task_id,
        "status": result.status,
        "title": normalized_title,
        "assignee": assignee,
        "audit_id": audit_id,
        "submitted_at": submitted_at,
    }


def _require_bob_tasks_enabled(settings: Settings) -> None:
    if not settings.allow_bob_tasks:
        raise BobTasksDisabled()


def validate_task_id(task_id: str) -> str:
    """Validate kanban task id from URL path."""
    if task_id is None:
        raise InvalidTaskId("task_id is required")
    normalized = task_id.strip()
    if not normalized:
        raise InvalidTaskId("task_id is required")
    if len(normalized) > MAX_TASK_ID_LENGTH:
        raise InvalidTaskId(f"task_id must be at most {MAX_TASK_ID_LENGTH} characters")
    if any(char.isspace() for char in normalized) or "/" in normalized or "\\" in normalized:
        raise InvalidTaskId("task_id contains invalid characters")
    if "\n" in normalized or "\r" in normalized:
        raise InvalidTaskId("task_id must not contain newlines")
    if not _TASK_ID_PATTERN.match(normalized):
        raise InvalidTaskId("task_id format is invalid")
    return normalized


def clamp_list_limit(limit: int | None) -> int:
    if limit is None:
        return DEFAULT_LIST_LIMIT
    return max(1, min(int(limit), MAX_LIST_LIMIT))


def list_kanban_argv(settings: Settings) -> list[str]:
    """Return fixed argv for hermes kanban list --json."""
    return [settings.hermes_cli_bin, "kanban", "list", "--json"]


def show_kanban_argv(settings: Settings, task_id: str) -> list[str]:
    """Return fixed argv for hermes kanban show <id> --json."""
    validated = validate_task_id(task_id)
    return [settings.hermes_cli_bin, "kanban", "show", validated, "--json"]


def _is_no_such_task_message(text: str) -> bool:
    return "no such task" in text.lower()


def _run_kanban_read(
    settings: Settings,
    argv: list[str],
    *,
    runner: CommandRunner | None = None,
) -> KanbanReadResult:
    execute = runner or _default_runner
    try:
        completed = execute(argv, settings.bob_task_timeout_seconds)
    except FileNotFoundError:
        return KanbanReadResult(
            ok=False,
            exit_code=-1,
            stdout="",
            stderr="hermes CLI not found",
            detail="Hermes CLI unavailable",
        )
    except subprocess.TimeoutExpired:
        return KanbanReadResult(
            ok=False,
            exit_code=-1,
            stdout="",
            stderr="action timed out",
            detail="Kanban read timed out",
        )
    except OSError as exc:
        safe_detail = _sanitize_detail(str(exc))
        return KanbanReadResult(
            ok=False,
            exit_code=-1,
            stdout="",
            stderr=safe_detail,
            detail=safe_detail or "Kanban read failed",
        )

    stdout = completed.stdout.strip()
    stderr = completed.stderr.strip()
    combined = f"{stdout}\n{stderr}".strip()
    if _is_no_such_task_message(combined):
        return KanbanReadResult(
            ok=False,
            exit_code=completed.returncode,
            stdout=stdout,
            stderr=stderr,
            detail="Task not found",
            not_found=True,
        )

    if completed.returncode != 0:
        stderr_detail = _sanitize_detail(stderr) if stderr else None
        if not stderr_detail:
            stderr_detail = f"hermes kanban exited with code {completed.returncode}"
        return KanbanReadResult(
            ok=False,
            exit_code=completed.returncode,
            stdout=stdout,
            stderr=stderr,
            detail=stderr_detail,
        )

    if not stdout or not (stdout.startswith("{") or stdout.startswith("[")):
        if _is_no_such_task_message(stdout or stderr):
            return KanbanReadResult(
                ok=False,
                exit_code=completed.returncode,
                stdout=stdout,
                stderr=stderr,
                detail="Task not found",
                not_found=True,
            )
        return KanbanReadResult(
            ok=False,
            exit_code=completed.returncode,
            stdout=stdout,
            stderr=stderr,
            detail="Unexpected kanban output",
        )

    return KanbanReadResult(
        ok=True,
        exit_code=completed.returncode,
        stdout=stdout,
        stderr=stderr,
    )


def _parse_list_stdout(stdout: str) -> list[dict[str, Any]]:
    try:
        payload = json.loads(stdout)
    except json.JSONDecodeError as exc:
        raise ValueError("invalid kanban list JSON output") from exc
    if not isinstance(payload, list):
        raise ValueError("kanban list output must be a JSON array")
    tasks: list[dict[str, Any]] = []
    for item in payload:
        if isinstance(item, dict):
            tasks.append(item)
    return tasks


def _parse_show_stdout(stdout: str) -> dict[str, Any]:
    try:
        payload = json.loads(stdout)
    except json.JSONDecodeError as exc:
        raise ValueError("invalid kanban show JSON output") from exc
    if not isinstance(payload, dict):
        raise ValueError("kanban show output must be a JSON object")
    task = payload.get("task")
    if not isinstance(task, dict):
        raise ValueError("kanban show output missing task object")
    task_id = task.get("id")
    if not task_id or not isinstance(task_id, str):
        raise ValueError("kanban show output missing task id")
    return payload


def run_list_kanban_tasks(
    settings: Settings,
    *,
    runner: CommandRunner | None = None,
) -> KanbanReadResult:
    """Run list_kanban_tasks with fixed argv."""
    _require_bob_tasks_enabled(settings)
    argv = list_kanban_argv(settings)
    result = _run_kanban_read(settings, argv, runner=runner)
    if not result.ok:
        return result
    try:
        _parse_list_stdout(result.stdout)
    except ValueError as exc:
        return KanbanReadResult(
            ok=False,
            exit_code=result.exit_code,
            stdout=result.stdout,
            stderr=result.stderr,
            detail=_sanitize_detail(str(exc)),
        )
    return result


def run_show_kanban_task(
    settings: Settings,
    task_id: str,
    *,
    runner: CommandRunner | None = None,
) -> KanbanReadResult:
    """Run show_kanban_task with fixed argv."""
    _require_bob_tasks_enabled(settings)
    validate_task_id(task_id)
    argv = show_kanban_argv(settings, task_id)
    result = _run_kanban_read(settings, argv, runner=runner)
    if not result.ok:
        return result
    try:
        _parse_show_stdout(result.stdout)
    except ValueError as exc:
        return KanbanReadResult(
            ok=False,
            exit_code=result.exit_code,
            stdout=result.stdout,
            stderr=result.stderr,
            detail=_sanitize_detail(str(exc)),
        )
    return result


def build_task_list_response(
    settings: Settings,
    *,
    limit: int | None = None,
    runner: CommandRunner | None = None,
) -> dict[str, Any]:
    """List kanban tasks and return structured API payload."""
    _require_bob_tasks_enabled(settings)
    checked_at = datetime.now(timezone.utc).isoformat()
    bounded_limit = clamp_list_limit(limit)

    result = run_list_kanban_tasks(settings, runner=runner)
    if result.not_found:
        raise TaskNotFound()

    if not result.ok:
        return {
            "success": False,
            "error": "task_list_failed",
            "detail": result.detail or "Failed to list tasks",
            "checked_at": checked_at,
        }

    try:
        tasks = _parse_list_stdout(result.stdout)
    except ValueError as exc:
        return {
            "success": False,
            "error": "task_list_parse_failed",
            "detail": _sanitize_detail(str(exc)),
            "checked_at": checked_at,
        }

    sliced = tasks[:bounded_limit]
    return {
        "success": True,
        "tasks": sliced,
        "count": len(sliced),
        "limit": bounded_limit,
        "checked_at": checked_at,
    }


def build_task_show_response(
    settings: Settings,
    task_id: str,
    *,
    runner: CommandRunner | None = None,
) -> dict[str, Any]:
    """Show one kanban task and return structured API payload."""
    _require_bob_tasks_enabled(settings)
    validated_id = validate_task_id(task_id)
    checked_at = datetime.now(timezone.utc).isoformat()

    result = run_show_kanban_task(settings, validated_id, runner=runner)
    if result.not_found:
        raise TaskNotFound()

    if not result.ok:
        return {
            "success": False,
            "error": "task_show_failed",
            "detail": result.detail or "Failed to load task",
            "task_id": validated_id,
            "checked_at": checked_at,
        }

    try:
        payload = _parse_show_stdout(result.stdout)
    except ValueError as exc:
        return {
            "success": False,
            "error": "task_show_parse_failed",
            "detail": _sanitize_detail(str(exc)),
            "task_id": validated_id,
            "checked_at": checked_at,
        }

    task = payload.get("task") or {}
    events = payload.get("events")
    comments = payload.get("comments")
    if not isinstance(events, list):
        events = []
    if not isinstance(comments, list):
        comments = []

    response: dict[str, Any] = {
        "success": True,
        "task_id": validated_id,
        "task": task,
        "events": events,
        "comments": comments,
        "checked_at": checked_at,
    }
    latest_summary = payload.get("latest_summary")
    if latest_summary is not None:
        response["latest_summary"] = latest_summary
    return response
