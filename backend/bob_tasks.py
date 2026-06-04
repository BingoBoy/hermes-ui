"""Allowlisted Bob task creation via Hermes kanban CLI."""

from __future__ import annotations

import hashlib
import json
import os
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
ALLOWED_ACTIONS = frozenset({CREATE_KANBAN_TASK_ACTION})

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
        "audit_id": audit_id,
        "submitted_at": submitted_at,
    }
