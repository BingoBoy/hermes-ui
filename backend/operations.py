"""Read-only operational status for LaunchAgents and optional Docker."""

from __future__ import annotations

import os
import plistlib
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from backend.config import Settings
from backend.status import _launchctl_status, _run_read_only

_TUNNEL_DISCLAIMER = (
    "Lokal observasjon av cloudflared og HTTP-probe. "
    "Viser ikke full Cloudflare edge-status."
)
_PROCESS_SUMMARY_MAX = 120
_TOKEN_ARG_RE = re.compile(r"--token\s+\S+")
_JWT_RE = re.compile(r"eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+(?:\.[A-Za-z0-9_-]+)?")


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


def _sanitize_process_summary(line: str) -> str:
    cleaned = line.strip()
    if ".cloudflared/" in cleaned:
        idx = cleaned.find(".cloudflared/")
        cleaned = cleaned[:idx] + ".cloudflared/[redacted]"
    cleaned = _TOKEN_ARG_RE.sub("--token [redacted]", cleaned)
    cleaned = _JWT_RE.sub("[redacted]", cleaned)
    if len(cleaned) > _PROCESS_SUMMARY_MAX:
        return cleaned[: _PROCESS_SUMMARY_MAX - 3] + "..."
    return cleaned


def _parse_http_status_and_location(stdout: str) -> tuple[int | None, str | None]:
    status: int | None = None
    location_host: str | None = None
    for line in stdout.splitlines():
        stripped = line.strip()
        if stripped.upper().startswith("HTTP/"):
            match = re.match(r"HTTP/\d(?:\.\d)?\s+(\d{3})", stripped, re.IGNORECASE)
            if match:
                status = int(match.group(1))
        elif stripped.lower().startswith("location:"):
            location_value = stripped.split(":", 1)[1].strip()
            location_host = urlparse(location_value).hostname
    return status, location_host


def _cloudflared_binary_status(settings: Settings) -> dict[str, Any]:
    which = _run_read_only(["/usr/bin/which", "cloudflared"])
    binary_path = which.stdout.strip() if which.ok and which.stdout else ""
    if not binary_path and settings.hermes_cloudflared_bin:
        candidate = _expand_path(settings.hermes_cloudflared_bin)
        if Path(candidate).is_file():
            binary_path = candidate

    if not binary_path:
        return {
            "installed": False,
            "binary_path": None,
            "version": None,
            "error": which.stderr or "cloudflared not found",
        }

    version = _run_read_only([binary_path, "--version"], timeout=3.0)
    return {
        "installed": True,
        "binary_path": binary_path,
        "version": version.stdout if version.stdout else None,
        "error": None if version.stdout else (version.stderr or "version check failed"),
    }


def _cloudflared_process_status() -> dict[str, Any]:
    result = _run_read_only(["/usr/bin/pgrep", "-lf", "cloudflared"], timeout=2.0)
    if not result.stdout:
        return {
            "process_running": False,
            "process_summary": None,
            "error": None if result.ok else (result.stderr or "pgrep failed"),
        }

    first_line = result.stdout.splitlines()[0]
    return {
        "process_running": True,
        "process_summary": _sanitize_process_summary(first_line),
        "error": None,
    }


def _edge_probe_status(settings: Settings) -> dict[str, Any]:
    if not settings.hermes_ops_edge_probe:
        return {
            "enabled": False,
            "attempted": False,
            "http_status": None,
            "access_redirect": False,
            "location_host": None,
            "error": None,
        }

    hostname = settings.hermes_public_hostname.strip()
    if not hostname:
        return {
            "enabled": True,
            "attempted": False,
            "http_status": None,
            "access_redirect": False,
            "location_host": None,
            "error": "public hostname not configured",
        }

    url = f"https://{hostname}/api/status"
    result = _run_read_only(
        [
            "/usr/bin/curl",
            "-sS",
            "-D",
            "-",
            "-o",
            "/dev/null",
            "--max-time",
            "5",
            "--max-redirs",
            "0",
            url,
        ],
        timeout=6.0,
    )
    http_status, location_host = _parse_http_status_and_location(result.stdout)
    error = None
    if http_status is None:
        error = result.stderr or "could not parse HTTP status from edge probe"

    access_redirect = bool(
        http_status == 302
        and location_host
        and "cloudflareaccess.com" in location_host.lower()
    )
    return {
        "enabled": True,
        "attempted": True,
        "http_status": http_status,
        "access_redirect": access_redirect,
        "location_host": location_host,
        "error": error,
    }


def _cloudflared_launchctl_status(settings: Settings) -> dict[str, Any]:
    label = settings.hermes_cloudflared_launchd_label.strip()
    if not label:
        return {
            "included": False,
            "reason": "no stable cloudflared LaunchAgent label configured",
        }

    launchctl_list = _launchctl_status(label)
    launchctl_print = _launchctl_print_state(label)
    running = bool(
        launchctl_list.get("matched")
        or launchctl_print.get("state") == "running"
    )
    return {
        "included": True,
        "label": label,
        "running": running,
        "launchctl_list": launchctl_list,
        "launchctl_print": launchctl_print,
    }


def _cloudflare_tunnel_status(settings: Settings) -> dict[str, Any]:
    binary = _cloudflared_binary_status(settings)
    process = _cloudflared_process_status()
    return {
        "observation_scope": "local_agent_and_edge_probe",
        "disclaimer": _TUNNEL_DISCLAIMER,
        "public_hostname": settings.hermes_public_hostname,
        "tunnel_name": settings.hermes_cloudflare_tunnel_name,
        "service_target": f"http://{settings.host}:{settings.port}",
        "cloudflared": {
            "installed": binary["installed"],
            "binary_path": binary["binary_path"],
            "version": binary["version"],
            "process_running": process["process_running"],
            "process_summary": process["process_summary"],
            "error": binary.get("error") or process.get("error"),
        },
        "edge_probe": _edge_probe_status(settings),
        "launchctl": _cloudflared_launchctl_status(settings),
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
        "cloudflare_tunnel": _cloudflare_tunnel_status(settings),
        "checked_at": datetime.now(timezone.utc).isoformat(),
    }
