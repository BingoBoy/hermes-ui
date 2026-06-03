# Logs API Plan

## Status

Planning only. No logs API route is implemented yet.

## Future Endpoint

```text
GET /api/logs/{log_id}?lines=100
```

## Contract

- `log_id` maps to a server-side allowlist entry.
- The client never sends a path.
- `lines` is optional and bounded.
- Default line count should be 100.
- Maximum line count should be 500 unless a source has a lower limit.
- Returned log lines are redacted before JSON serialization.

## Example Success Response

```json
{
  "success": true,
  "log_id": "hermes_gateway_stdout",
  "display_name": "Hermes gateway output",
  "lines": 100,
  "redacted": true,
  "content": [
    "..."
  ]
}
```

## Example Safe Error Response

```json
{
  "success": false,
  "log_id": "hermes_gateway_stdout",
  "error": "log_file_unavailable",
  "details": "The configured log file is not readable or does not exist."
}
```

## Explicit Non-Goals

The logs API must not support:

- Paths from client input
- Glob patterns from client input
- Reading arbitrary files
- Writing, truncating, rotating, or deleting logs
- Shell command execution
- Start, stop, or restart actions

