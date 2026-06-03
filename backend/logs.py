"""Read-only bounded log retrieval from allowlisted sources."""

from __future__ import annotations

from collections import deque
from datetime import datetime, timezone
from pathlib import Path

from backend.log_sources import (
    DEFAULT_LOG_LINES,
    LogSource,
    clamp_lines,
    get_source_by_id,
    list_sources_metadata,
)
from backend.redaction import redact_lines


def read_tail_lines(path: Path, lines: int, *, max_read_bytes: int = 512_000) -> list[str]:
    """Read the last N lines from a file without loading the entire file."""
    if lines <= 0:
        return []

    with path.open("rb") as handle:
        handle.seek(0, 2)
        file_size = handle.tell()
        if file_size == 0:
            return []

        offset = min(file_size, max_read_bytes)
        handle.seek(-offset, 2)
        chunk = handle.read().decode("utf-8", errors="replace")

    return chunk.splitlines()[-lines:]


def get_logs_sources_payload() -> dict[str, object]:
    return {
        "read_only": True,
        "sources": list_sources_metadata(),
    }


def get_log_content(source_id: str, requested_lines: int = DEFAULT_LOG_LINES) -> dict[str, object] | None:
    """
    Return log payload for an allowlisted source_id.

    Returns None when source_id is unknown or disabled.
    """
    source = get_source_by_id(source_id)
    if source is None:
        return None

    line_count = clamp_lines(requested_lines, source)
    path = Path(source.absolute_path)

    if not path.is_file():
        return _unavailable_payload(source, line_count, "log_file_unavailable")

    try:
        raw_lines = read_tail_lines(path, line_count)
    except OSError:
        return _unavailable_payload(source, line_count, "log_file_unreadable")

    content = redact_lines(raw_lines) if source.requires_redaction else raw_lines

    return {
        "success": True,
        "source_id": source.source_id,
        "display_name": source.display_name,
        "lines": line_count,
        "returned_lines": len(content),
        "redacted": source.requires_redaction,
        "read_only": True,
        "content": content,
        "checked_at": datetime.now(timezone.utc).isoformat(),
    }


def _unavailable_payload(source: LogSource, line_count: int, error: str) -> dict[str, object]:
    return {
        "success": False,
        "source_id": source.source_id,
        "display_name": source.display_name,
        "lines": line_count,
        "redacted": True,
        "read_only": True,
        "error": error,
        "details": "The configured log file is not readable or does not exist.",
        "checked_at": datetime.now(timezone.utc).isoformat(),
    }
