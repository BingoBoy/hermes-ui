"""Read-only operational status for LaunchAgents and optional Docker."""

from __future__ import annotations

import os
import plistlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from backend.config import Settings
from backend.status import _launchctl_status, _run_read_only


def _expand_path(path: str) -> str:
    return os.path.expanduser(path.strip())


def _program_summary(program_arguments: Any) -> str | None:
    if not isinstance(program_arguments, list) or not program_arguments:
        return None
    parts = [str(item) for item in program_arguments]
    summary = " ".join(parts)
    if len(summary) > 200:
        return summary[:197] + "..."
    return summary


def _read_plist_metadata(plist_path: str) -> dict[str, Any]:
    expanded = _expand_path(plist_path)
    path = Path(expanded)
    if not path.is_file():
        return {
            "readable": False,
            "plist_path": expanded,
            "error": "plist not found",
        }

    try:
        with path.open("rb") as handle:
            data = plistlib.load(handle)
    except (OSError, plistlib.InvalidFileException, ValueError) as exc:
        return {
            "readable": False,
            "plist_path": expanded,
            "error": str(exc),
        }

    if not isinstance(data, dict):
        return {
            "readable": False,
            "plist_path": expanded,
            "error": "invalid plist structure",
        }

    env = data.get("EnvironmentVariables")
    env_keys: list[str] = []
    if isinstance(env, dict):
        env_keys = sorted(str(key) for key in env.keys())

    log_paths: dict[str, str | None] = {
        "stdout": None,
        "stderr": None,
    }
    for key, target in (("stdout", "StandardOutPath"), ("stderr", "StandardErrorPath")):
        value = data.get(target)
        if isinstance(value, str) and value.strip():
            log_paths[key] = value.strip()

    working_directory = data.get("WorkingDirectory")
    return {
        "readable": True,
        "plist_path": expanded,
        "label": data.get("Label") if isinstance(data.get("Label"), str) else None,
        "program_summary": _program_summary(data.get("ProgramArguments")),
        "log_paths": log_paths,
        "working_directory": (
            working_directory.strip()
            if isinstance(working_directory, str) and working_directory.strip()
            else None
        ),
        "environment_variable_keys": env_keys,
    }


def _launchctl_print_state(label: str) -> dict[str, Any]:
    target = f"gui/{os.getuid()}/{label}"
    result = _run_read_only(["launchctl", "print", target], timeout=3.0)
    if not result.ok:
        return {
            "available": False,
            "domain": target,
            "detail": result.stderr or "launchctl print failed",
        }

    state = "unknown"
    for line in result.stdout.splitlines():
        stripped = line.strip()
        if stripped.startswith("state = "):
            state = stripped.split("state = ", 1)[1].strip()
            break

    return {
        "available": True,
        "domain": target,
        "state": state,
    }


def _build_launch_agent(
    settings: Settings,
    *,
    agent_id: str,
    label: str,
    plist_path: str,
) -> dict[str, Any]:
    plist = _read_plist_metadata(plist_path)
    launchctl_list = _launchctl_status(label)
    launchctl_print = _launchctl_print_state(label)
    running = bool(
        launchctl_list.get("matched")
        or launchctl_print.get("state") == "running"
    )

    return {
        "id": agent_id,
        "label": label,
        "plist_path": plist.get("plist_path", _expand_path(plist_path)),
        "plist": plist,
        "launchctl_list": launchctl_list,
        "launchctl_print": launchctl_print,
        "running": running,
    }


def _docker_status(include_docker: bool) -> dict[str, Any]:
    if not include_docker:
        return {
            "included": False,
            "reason": "disabled_by_config",
        }

    which = _run_read_only(["/usr/bin/which", "docker"])
    if not which.ok or not which.stdout:
        return {
            "included": True,
            "available": False,
            "detail": "docker not installed",
        }

    version = _run_read_only(
        ["docker", "info", "--format", "{{.ServerVersion}}"],
        timeout=3.0,
    )
    containers = _run_read_only(
        ["docker", "ps", "--format", "{{.Names}}"],
        timeout=3.0,
    )
    names: list[str] = []
    if containers.ok and containers.stdout:
        names = [
            line.strip()
            for line in containers.stdout.splitlines()
            if line.strip()
        ][:10]

    return {
        "included": True,
        "available": version.ok,
        "server_version": version.stdout if version.ok else None,
        "container_count": len(names),
        "containers": names,
        "detail": None if version.ok else (version.stderr or "docker info failed"),
    }


def get_operations_status(settings: Settings) -> dict[str, Any]:
    """Return read-only LaunchAgent and optional Docker operational details."""
    return {
        "read_only": True,
        "launch_agents": [
            _build_launch_agent(
                settings,
                agent_id="hermes-ui",
                label=settings.hermes_ui_launchd_label,
                plist_path=settings.hermes_ui_plist_path,
            ),
            _build_launch_agent(
                settings,
                agent_id="hermes-gateway",
                label=settings.hermes_launchd_label,
                plist_path=settings.hermes_gateway_plist_path,
            ),
        ],
        "docker": _docker_status(settings.hermes_ops_include_docker),
        "checked_at": datetime.now(timezone.utc).isoformat(),
    }
