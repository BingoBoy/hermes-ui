"""Read-only status providers for Bob and Hermes."""

from __future__ import annotations

import os
import platform
import shutil
import socket
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any

from backend.config import Settings


@dataclass(frozen=True)
class CommandResult:
    ok: bool
    stdout: str
    stderr: str


def _run_read_only(args: list[str], timeout: float = 2.0) -> CommandResult:
    """Run a fixed local inspection command without shell interpolation."""
    try:
        completed = subprocess.run(
            args,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except FileNotFoundError:
        return CommandResult(ok=False, stdout="", stderr=f"{args[0]} not found")
    except subprocess.TimeoutExpired:
        return CommandResult(ok=False, stdout="", stderr=f"{args[0]} timed out")
    except OSError as exc:
        return CommandResult(ok=False, stdout="", stderr=str(exc))

    return CommandResult(
        ok=completed.returncode == 0,
        stdout=completed.stdout.strip(),
        stderr=completed.stderr.strip(),
    )


def _percent_used(used: int, total: int) -> str:
    if total <= 0:
        return "unknown"
    return f"{round((used / total) * 100)}%"


def _disk_usage() -> dict[str, str]:
    usage = shutil.disk_usage("/")
    return {
        "total": str(usage.total),
        "used": str(usage.used),
        "free": str(usage.free),
        "percent_used": _percent_used(usage.used, usage.total),
    }


def _memory_usage() -> dict[str, str]:
    # macOS exposes page counts through vm_stat. Keep this best-effort and safe.
    vm_stat = _run_read_only(["vm_stat"])
    if not vm_stat.ok:
        return {"percent_used": "unknown", "detail": vm_stat.stderr or "vm_stat unavailable"}

    page_size = 4096
    pages: dict[str, int] = {}
    for line in vm_stat.stdout.splitlines():
        if ":" not in line:
            continue
        name, raw_value = line.split(":", 1)
        clean_value = raw_value.strip().rstrip(".")
        if clean_value.isdigit():
            pages[name.strip()] = int(clean_value)

    free = pages.get("Pages free", 0) + pages.get("Pages speculative", 0)
    active = pages.get("Pages active", 0)
    inactive = pages.get("Pages inactive", 0)
    wired = pages.get("Pages wired down", 0)
    compressed = pages.get("Pages occupied by compressor", 0)
    used = active + inactive + wired + compressed
    total = used + free

    return {
        "percent_used": _percent_used(used, total),
        "page_size": str(page_size),
        "detail": "macOS vm_stat",
    }


def _uptime() -> str:
    uptime = _run_read_only(["uptime"])
    if not uptime.ok:
        return "unknown"
    return uptime.stdout


def get_system_status(settings: Settings) -> dict[str, Any]:
    """Return safe read-only system information."""
    hostname = settings.bob_hostname or socket.gethostname()
    return {
        "hostname": hostname,
        "platform": platform.platform(),
        "python_version": platform.python_version(),
        "uptime": _uptime(),
        "disk": _disk_usage(),
        "memory": _memory_usage(),
        "checked_at": datetime.now(timezone.utc).isoformat(),
    }


def _launchctl_status(label: str) -> dict[str, Any]:
    result = _run_read_only(["launchctl", "list"])
    if not result.ok:
        return {
            "available": False,
            "matched": False,
            "detail": result.stderr or "launchctl unavailable",
        }

    for line in result.stdout.splitlines():
        if label in line:
            parts = line.split()
            pid = parts[0] if parts and parts[0] != "-" else None
            return {
                "available": True,
                "matched": True,
                "pid": int(pid) if pid and pid.isdigit() else None,
                "raw_status": line,
            }

    return {
        "available": True,
        "matched": False,
        "detail": f"{label} not present in launchctl list",
    }


def _process_status() -> dict[str, Any]:
    result = _run_read_only(["ps", "-ax", "-o", "pid=,command="])
    if not result.ok:
        return {
            "available": False,
            "matched": False,
            "detail": result.stderr or "process list unavailable",
        }

    matches: list[dict[str, Any]] = []
    for line in result.stdout.splitlines():
        normalized = line.lower()
        if "hermes" not in normalized:
            continue
        if "hermes-ui" in normalized:
            continue
        if "hermes_cli" not in normalized and "hermes-agent" not in normalized and "ai.hermes" not in normalized:
            continue

        pid_text, _, command = line.strip().partition(" ")
        matches.append(
            {
                "pid": int(pid_text) if pid_text.isdigit() else None,
                "command_hint": command[:160],
            }
        )

    return {
        "available": True,
        "matched": bool(matches),
        "matches": matches,
    }


def get_hermes_status(settings: Settings) -> dict[str, Any]:
    """Return read-only Hermes gateway status with safe degradation."""
    launchctl = _launchctl_status(settings.hermes_launchd_label)
    process = _process_status()
    running = bool(launchctl.get("matched") or process.get("matched"))
    state = "running" if running else "not_detected"

    return {
        "service": "hermes",
        "read_only": True,
        "running": running,
        "state": state,
        "launchd_label": settings.hermes_launchd_label,
        "launchctl": launchctl,
        "process": process,
        "last_checked": datetime.now(timezone.utc).isoformat(),
    }


def get_service_status(settings: Settings) -> dict[str, Any]:
    """Return read-only Hermes UI service status."""
    return {
        "status": "ok",
        "service": settings.service_name,
        "version": settings.version,
        "host": settings.bob_hostname or socket.gethostname(),
        "bind_host": settings.host,
        "bind_port": settings.port,
        "read_only": True,
        "allow_unsafe_commands": settings.allow_unsafe_commands,
        "checked_at": datetime.now(timezone.utc).isoformat(),
    }


def as_jsonable(payload: Any) -> Any:
    if hasattr(payload, "__dataclass_fields__"):
        return asdict(payload)
    return payload

