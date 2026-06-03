"""Redact sensitive values from log lines before API or UI exposure."""

from __future__ import annotations

import re
from typing import Iterable

REDACTED = "[REDACTED]"

_PRIVATE_KEY_BEGIN = re.compile(
    r"-----BEGIN (?:RSA |OPENSSH |EC |DSA )?PRIVATE KEY-----",
    re.IGNORECASE,
)
_PRIVATE_KEY_END = re.compile(r"-----END (?:RSA |OPENSSH |EC |DSA )?PRIVATE KEY-----", re.IGNORECASE)

_LINE_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"Bearer\s+\S+", re.IGNORECASE),
    re.compile(r"(?i)\b(api[_-]?key|token|password|secret|authorization)\b\s*[:=]\s*\S+"),
    re.compile(r"(?i)\b(cloudflare|tunnel_secret|access_token|client_secret)\b\s*[:=]\s*\S+"),
    re.compile(r"(?i)^\s*[A-Z0-9_]*(TOKEN|SECRET|PASSWORD|API_KEY|AUTHORIZATION)[A-Z0-9_]*\s*=\s*\S+"),
    re.compile(r"(?i)^\s*export\s+[A-Z0-9_]*(TOKEN|SECRET|PASSWORD|API_KEY)[A-Z0-9_]*\s*="),
)


def _redact_known_patterns(line: str) -> str:
    redacted = line
    for pattern in _LINE_PATTERNS:
        redacted = pattern.sub(REDACTED, redacted)
    return redacted


def redact_line(line: str, *, in_private_key_block: bool) -> tuple[str, bool]:
    """Return redacted line and whether the reader remains inside a private key block."""
    stripped = line.rstrip("\n")

    if in_private_key_block:
        if _PRIVATE_KEY_END.search(stripped):
            return REDACTED, False
        return REDACTED, True

    if _PRIVATE_KEY_BEGIN.search(stripped):
        if _PRIVATE_KEY_END.search(stripped):
            return REDACTED, False
        return REDACTED, True

    if stripped.strip().startswith("#") and "=" in stripped:
        return REDACTED, False

    lowered = stripped.lower()
    if lowered.startswith(".env") or " dotenv" in lowered:
        return REDACTED, False

    redacted = _redact_known_patterns(stripped)
    if any(marker in lowered for marker in ("private key", "cloudflare credentials", "api key")):
        return REDACTED, False

    return redacted, False


def redact_lines(lines: Iterable[str]) -> list[str]:
    """Redact an iterable of log lines."""
    output: list[str] = []
    in_private_key_block = False

    for line in lines:
        redacted, in_private_key_block = redact_line(line, in_private_key_block=in_private_key_block)
        output.append(redacted)

    return output
