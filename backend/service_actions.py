"""Allowlisted service actions for Hermes Gateway only."""

from __future__ import annotations

import json
import os
import secrets
import subprocess
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from backend.config import Settings
from backend.redaction import redact_line
from backend.status import get_hermes_status

ALLOWED_GATEWAY_LABEL = "ai.hermes.gateway"
RESTART_ACTION = "restart_hermes_gateway"
ALLOWED_ACTIONS = frozenset({RESTART_ACTION})

ACTION_TIMEOUT_SECONDS = 5.0
COOLDOWN_SECONDS = 30
MAX_DETAIL_LENGTH = 200

DEFAULT_AUDIT_LOG = "/Users/trulsdahl/.hermes-ui/logs/service-actions.log"

CommandRunner = Callable[[list[str], float], subprocess.CompletedProcess[str]]

_last_restart_at: float | None = None


class ServiceActionsDisabled(Exception):
    """Raised when ALLOW_SERVICE_ACTIONS is false."""


class ActionNotAllowed(Exception):
    """Raised when an action is not in the allowlist."""


class CooldownActive(Exception):
    """Raised when restart was requested too recently."""

    def __init__(self, retry_after: int) -> None:
        self.retry_after = retry_after
        super().__init__(f"Cooldown active; retry in {retry_after} seconds")


@dataclass(frozen=True)
class ActionResult:
    ok: bool
    exit_code: int
    stdout: str
    stderr: str
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
    raw = os.getenv("HERMES_UI_AUDIT_LOG", DEFAULT_AUDIT_LOG).strip()
    return Path(raw or DEFAULT_AUDIT_LOG)


def _sanitize_detail(text: str, *, max_length: int = MAX_DETAIL_LENGTH) -> str:
    redacted, _ = redact_line(text.strip(), in_private_key_block=False)
    if len(redacted) > max_length:
        return redacted[: max_length - 3] + "..."
    return redacted


def _make_audit_id(action: str) -> str:
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return f"{timestamp}-{action}-{secrets.token_hex(4)}"


def _validate_gateway_label(settings: Settings) -> None:
    if settings.hermes_launchd_label != ALLOWED_GATEWAY_LABEL:
        raise ActionNotAllowed(
            f"Service actions are restricted to {ALLOWED_GATEWAY_LABEL} only"
        )


def restart_argv(settings: Settings) -> list[str]:
    """Return the fixed launchctl argv for gateway restart."""
    _validate_gateway_label(settings)
    uid = os.getuid()
    return [
        "launchctl",
        "kickstart",
        "-k",
        f"gui/{uid}/{ALLOWED_GATEWAY_LABEL}",
    ]


def write_audit_entry(
    settings: Settings,
    *,
    audit_id: str,
    action: str,
    success: bool,
    exit_code: int | None,
    detail: str | None,
    audit_path: Path | None = None,
) -> None:
    """Append one JSONL audit record."""
    path = audit_path or _audit_log_path(settings)
    path.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "audit_id": audit_id,
        "action": action,
        "target_label": ALLOWED_GATEWAY_LABEL,
        "actor": "hermes-ui",
        "auth_layer": "cloudflare-access",
        "success": success,
        "exit_code": exit_code,
        "detail": detail,
    }
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=True) + "\n")


def _check_cooldown(now: float | None = None) -> None:
    global _last_restart_at
    current = now if now is not None else time.monotonic()
    if _last_restart_at is None:
        return
    elapsed = current - _last_restart_at
    if elapsed < COOLDOWN_SECONDS:
        retry_after = max(1, int(COOLDOWN_SECONDS - elapsed))
        raise CooldownActive(retry_after)


def _mark_restart(now: float | None = None) -> None:
    global _last_restart_at
    _last_restart_at = now if now is not None else time.monotonic()


def reset_restart_cooldown() -> None:
    """Reset cooldown state — intended for tests."""
    global _last_restart_at
    _last_restart_at = None


def run_allowlisted_action(
    action: str,
    settings: Settings,
    *,
    runner: CommandRunner | None = None,
    audit_path: Path | None = None,
    now: float | None = None,
) -> ActionResult:
    """Execute one allowlisted action with fixed argv and no shell."""
    if not settings.allow_service_actions:
        raise ServiceActionsDisabled()

    if action not in ALLOWED_ACTIONS:
        raise ActionNotAllowed(f"Unknown or disallowed action: {action}")

    if action == RESTART_ACTION:
        _check_cooldown(now)
        argv = restart_argv(settings)
    else:
        raise ActionNotAllowed(f"Unknown or disallowed action: {action}")

    execute = runner or _default_runner
    try:
        completed = execute(argv, ACTION_TIMEOUT_SECONDS)
    except FileNotFoundError:
        return ActionResult(
            ok=False,
            exit_code=-1,
            stdout="",
            stderr="launchctl not found",
            detail="launchctl unavailable",
        )
    except subprocess.TimeoutExpired:
        return ActionResult(
            ok=False,
            exit_code=-1,
            stdout="",
            stderr="action timed out",
            detail="Action timed out",
        )
    except OSError as exc:
        safe_detail = _sanitize_detail(str(exc))
        return ActionResult(
            ok=False,
            exit_code=-1,
            stdout="",
            stderr=safe_detail,
            detail=safe_detail or "Action failed",
        )

    stderr_detail = _sanitize_detail(completed.stderr) if completed.stderr else None
    if completed.returncode != 0 and not stderr_detail:
        stderr_detail = f"launchctl exited with code {completed.returncode}"

    if action == RESTART_ACTION and completed.returncode == 0:
        _mark_restart(now)

    return ActionResult(
        ok=completed.returncode == 0,
        exit_code=completed.returncode,
        stdout=completed.stdout.strip(),
        stderr=completed.stderr.strip(),
        detail=stderr_detail,
    )


def build_restart_response(
    settings: Settings,
    *,
    runner: CommandRunner | None = None,
    audit_path: Path | None = None,
    now: float | None = None,
) -> dict[str, Any]:
    """Run restart and return structured API payload."""
    audit_id = _make_audit_id("restart")
    checked_at = datetime.now(timezone.utc).isoformat()

    if not settings.allow_service_actions:
        raise ServiceActionsDisabled()

    try:
        result = run_allowlisted_action(
            RESTART_ACTION,
            settings,
            runner=runner,
            audit_path=audit_path,
            now=now,
        )
    except CooldownActive as exc:
        write_audit_entry(
            settings,
            audit_id=audit_id,
            action=RESTART_ACTION,
            success=False,
            exit_code=None,
            detail=f"cooldown_active:{exc.retry_after}s",
            audit_path=audit_path,
        )
        raise

    write_audit_entry(
        settings,
        audit_id=audit_id,
        action=RESTART_ACTION,
        success=result.ok,
        exit_code=result.exit_code,
        detail=result.detail,
        audit_path=audit_path,
    )

    hermes_status = get_hermes_status(settings)
    payload: dict[str, Any] = {
        "action": "restart",
        "success": result.ok,
        "message": (
            "Hermes Gateway restart command completed"
            if result.ok
            else "Hermes Gateway restart command failed"
        ),
        "service": "hermes",
        "launchd_label": ALLOWED_GATEWAY_LABEL,
        "audit_id": audit_id,
        "checked_at": checked_at,
        "hermes_status": hermes_status,
    }

    if not result.ok:
        payload["error"] = "action_failed"
        payload["detail"] = result.detail or "Action failed"

    if result.ok and not hermes_status.get("running"):
        payload["warning"] = "service not detected after restart"

    return payload
