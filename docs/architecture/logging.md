# Logging Architecture: Verified Logs Viewer

## Purpose

This document defines the safe logging model for the Hermes UI log viewer.

## Verified Sources on Bob

The Hermes LaunchAgent was inspected read-only via `BobRemote`.

| Field | Verified value |
|-------|----------------|
| Hostname | `Truls-sin-Mac-mini.local` |
| User | `trulsdahl` |
| LaunchAgent plist | `/Users/trulsdahl/Library/LaunchAgents/ai.hermes.gateway.plist` |
| Label | `ai.hermes.gateway` |
| WorkingDirectory | `/Users/trulsdahl/.hermes/hermes-agent` |
| Program | `/Users/trulsdahl/.hermes/hermes-agent/venv/bin/python -m hermes_cli.main gateway run --replace` |
| StandardOutPath | `/Users/trulsdahl/.hermes/logs/gateway.log` |
| StandardErrorPath | `/Users/trulsdahl/.hermes/logs/gateway.error.log` |

## Allowlist Model

The log viewer uses a static server-side allowlist. The browser may request a `source_id`, but it must never provide a file path.

Each log source must define:

| Field | Description |
|-------|-------------|
| `source_id` | Stable machine-readable ID used in API routes |
| `display_name` | Human-friendly UI label |
| `absolute_path` | Verified absolute file path on Bob |
| `max_lines` | Hard upper bound for returned lines |
| `requires_redaction` | Whether every line must pass redaction |
| `phase_status` | `verified`, `candidate`, or `tbd` |

## Active Allowlist

| source_id | display_name | absolute_path | max_lines | requires_redaction | status |
|-----------|--------------|---------------|-----------|--------------------|--------|
| `gateway_stdout` | Hermes gateway output | `/Users/trulsdahl/.hermes/logs/gateway.log` | 500 | yes | enabled |
| `gateway_stderr` | Hermes gateway errors | `/Users/trulsdahl/.hermes/logs/gateway.error.log` | 500 | yes | enabled |
| `agent` | Hermes agent log | `/Users/trulsdahl/.hermes/logs/agent.log` | 500 | yes | disabled |
| `errors` | Hermes errors log | `/Users/trulsdahl/.hermes/logs/errors.log` | 500 | yes | disabled |
| `hermes_ui_backend` | Hermes UI backend log | TBD | 500 | yes | tbd |

Only enabled sources are exposed through `/api/logs/sources`.

## Explicitly Excluded Sources

Do not expose these through the log viewer:

- `.env` or `.env.*`
- `.hermes_history`
- `.git/logs/**`
- source code files
- virtualenv files
- Cloudflare credential files
- SSH keys
- arbitrary paths from client input

## Access Pattern

Recommended future API shape:

```text
GET /api/logs/sources
GET /api/logs/{source_id}?lines=100
```

Rules:

- `source_id` must resolve to a server-side allowlist entry.
- `lines` must be an integer bounded between 1 and the source `max_lines`.
- Missing files should return a safe structured error.
- File contents must be read-only.
- Redaction must run before data is serialized to JSON.

