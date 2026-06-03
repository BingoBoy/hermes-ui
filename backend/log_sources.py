"""Server-side allowlist for bounded read-only log sources."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Iterable

DEFAULT_LOG_LINES = 100
MAX_LOG_LINES = 500

# Verified on Bob via LaunchAgent StandardOutPath / StandardErrorPath.
_DEFAULT_GATEWAY_STDOUT = "/Users/trulsdahl/.hermes/logs/gateway.log"
_DEFAULT_GATEWAY_STDERR = "/Users/trulsdahl/.hermes/logs/gateway.error.log"


@dataclass(frozen=True)
class LogSource:
    source_id: str
    display_name: str
    absolute_path: str
    max_lines: int
    requires_redaction: bool
    enabled: bool


def _path_from_env(name: str, default: str) -> str:
    value = os.getenv(name, default).strip()
    return value or default


def get_allowlist() -> tuple[LogSource, ...]:
    """Return the static allowlist. Only enabled sources are exposed via API."""
    return (
        LogSource(
            source_id="gateway_stdout",
            display_name="Hermes gateway output",
            absolute_path=_path_from_env("HERMES_GATEWAY_STDOUT_LOG", _DEFAULT_GATEWAY_STDOUT),
            max_lines=MAX_LOG_LINES,
            requires_redaction=True,
            enabled=True,
        ),
        LogSource(
            source_id="gateway_stderr",
            display_name="Hermes gateway errors",
            absolute_path=_path_from_env("HERMES_GATEWAY_STDERR_LOG", _DEFAULT_GATEWAY_STDERR),
            max_lines=MAX_LOG_LINES,
            requires_redaction=True,
            enabled=True,
        ),
        LogSource(
            source_id="agent",
            display_name="Hermes agent log",
            absolute_path=_path_from_env(
                "HERMES_AGENT_LOG",
                "/Users/trulsdahl/.hermes/logs/agent.log",
            ),
            max_lines=MAX_LOG_LINES,
            requires_redaction=True,
            enabled=False,
        ),
        LogSource(
            source_id="errors",
            display_name="Hermes errors log",
            absolute_path=_path_from_env(
                "HERMES_ERRORS_LOG",
                "/Users/trulsdahl/.hermes/logs/errors.log",
            ),
            max_lines=MAX_LOG_LINES,
            requires_redaction=True,
            enabled=False,
        ),
    )


def get_enabled_sources() -> list[LogSource]:
    return [source for source in get_allowlist() if source.enabled]


def get_source_by_id(source_id: str) -> LogSource | None:
    for source in get_allowlist():
        if source.source_id == source_id and source.enabled:
            return source
    return None


def clamp_lines(requested: int, source: LogSource) -> int:
    bounded = max(1, min(requested, MAX_LOG_LINES))
    return min(bounded, source.max_lines)


def list_sources_metadata() -> list[dict[str, object]]:
    return [
        {
            "source_id": source.source_id,
            "display_name": source.display_name,
            "max_lines": source.max_lines,
            "default_lines": DEFAULT_LOG_LINES,
            "requires_redaction": source.requires_redaction,
            "read_only": True,
        }
        for source in get_enabled_sources()
    ]
