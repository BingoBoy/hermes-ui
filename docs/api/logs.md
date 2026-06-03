# Logs API

## Status

Implemented as bounded read-only endpoints.

## Endpoints

```text
GET /api/logs/sources
GET /api/logs/{source_id}?lines=100
```

## Sources List

`GET /api/logs/sources` returns only enabled allowlisted sources. It does not expose absolute file paths.

Example:

```json
{
  "read_only": true,
  "sources": [
    {
      "source_id": "gateway_stdout",
      "display_name": "Hermes gateway output",
      "max_lines": 500,
      "default_lines": 100,
      "requires_redaction": true,
      "read_only": true
    }
  ]
}
```

## Log Content

`GET /api/logs/{source_id}?lines=100`

Rules:

- `source_id` must resolve to a server-side allowlist entry.
- The client never sends a path.
- `lines` is optional, defaults to `100`, maximum `500`.
- Returned lines are redacted before JSON serialization.

### Success Response

```json
{
  "success": true,
  "source_id": "gateway_stdout",
  "display_name": "Hermes gateway output",
  "lines": 50,
  "returned_lines": 12,
  "redacted": true,
  "read_only": true,
  "content": ["..."],
  "checked_at": "2026-06-03T16:42:29.128696+00:00"
}
```

### Unknown Source

HTTP `404`:

```json
{
  "detail": {
    "success": false,
    "error": "unknown_log_source",
    "details": "Unknown or disabled log source: example"
  }
}
```

### Missing Log File

HTTP `200` with safe structured error:

```json
{
  "success": false,
  "source_id": "gateway_stdout",
  "display_name": "Hermes gateway output",
  "lines": 50,
  "redacted": true,
  "read_only": true,
  "error": "log_file_unavailable",
  "details": "The configured log file is not readable or does not exist."
}
```

## Enabled Sources

| source_id | display_name | verified path on Bob |
|-----------|--------------|----------------------|
| `gateway_stdout` | Hermes gateway output | `/Users/trulsdahl/.hermes/logs/gateway.log` |
| `gateway_stderr` | Hermes gateway errors | `/Users/trulsdahl/.hermes/logs/gateway.error.log` |

Candidate sources such as `agent` and `errors` remain disabled until explicitly verified.

## Explicit Non-Goals

The logs API does not support:

- Paths from client input
- Glob patterns from client input
- Reading arbitrary files
- Writing, truncating, rotating, or deleting logs
- Shell command execution
- Start, stop, or restart actions
