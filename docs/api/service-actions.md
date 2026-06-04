# Service Actions API

Planned write endpoints for Hermes Gateway control. **Not implemented until Phase 5A execute.**

## Principles

- Fixed allowlisted actions only — no client-supplied commands or shell strings.
- Target service: Hermes Gateway (`ai.hermes.gateway`) only.
- Hermes UI LaunchAgent (`no.truls.hermes-ui`) is never controllable from the API.
- All write actions require `ALLOW_SERVICE_ACTIONS=true` on the server.
- All write actions are audit-logged append-only.
- Cloudflare Access remains the external authentication boundary.

## Feature Gate

| Variable | Default | Purpose |
|----------|---------|---------|
| `ALLOW_SERVICE_ACTIONS` | `false` | Master switch for POST service actions |
| `ALLOW_UNSAFE_COMMANDS` | `false` | Must remain `false`; unrelated escape hatch |

When disabled, write endpoints return:

```json
{
  "success": false,
  "error": "service_actions_disabled",
  "detail": "Write actions are disabled on this server"
}
```

HTTP status: `403`

## Verified Commands (Bob, 2026-06-04)

| Action | launchctl command | Verification status |
|--------|-------------------|---------------------|
| Status | `launchctl list` + match label | In production (read-only) |
| Status detail | `launchctl print gui/{uid}/ai.hermes.gateway` | Verified |
| Restart | `launchctl kickstart -k gui/{uid}/ai.hermes.gateway` | **Live verified** |
| Start | `launchctl bootstrap gui/{uid} {plist_path}` | Documented, not live-tested |
| Stop | `launchctl bootout gui/{uid} {plist_path}` | Documented, not live-tested |

Plist path: `/Users/trulsdahl/Library/LaunchAgents/ai.hermes.gateway.plist`

Implementation uses `subprocess.run` with a fixed argv list. No `shell=True`.

## Endpoints

### POST /api/hermes/restart (5A)

Restart the Hermes Gateway LaunchAgent.

**Request:** Empty body. No query parameters. No client command input.

**Success response (200):**

```json
{
  "action": "restart",
  "success": true,
  "message": "Hermes Gateway restart command completed",
  "service": "hermes",
  "launchd_label": "ai.hermes.gateway",
  "audit_id": "2026-06-04T10:15:00Z-restart-abc123",
  "checked_at": "2026-06-04T10:15:03+00:00",
  "hermes_status": {
    "running": true,
    "state": "running",
    "launchctl": { "matched": true, "pid": 53383 }
  }
}
```

**Failure response (502 or 500):**

```json
{
  "action": "restart",
  "success": false,
  "error": "action_failed",
  "detail": "launchctl exited with code 1",
  "service": "hermes",
  "launchd_label": "ai.hermes.gateway",
  "audit_id": "2026-06-04T10:15:00Z-restart-abc123",
  "checked_at": "2026-06-04T10:15:03+00:00"
}
```

**Rate limit (429):**

```json
{
  "success": false,
  "error": "cooldown_active",
  "detail": "Restart was requested recently; try again in 25 seconds"
}
```

### POST /api/hermes/start (5B — planned)

Not implemented in 5A.

### POST /api/hermes/stop (5B — planned)

Not implemented in 5A.

## Audit Log

Path (default): `/Users/trulsdahl/.hermes-ui/logs/service-actions.log`

Override: `HERMES_UI_AUDIT_LOG`

Format: JSONL — one JSON object per line.

Example entry:

```json
{
  "timestamp": "2026-06-04T10:15:00.123456+00:00",
  "audit_id": "2026-06-04T10:15:00Z-restart-abc123",
  "action": "restart",
  "target_label": "ai.hermes.gateway",
  "actor": "hermes-ui",
  "auth_layer": "cloudflare-access",
  "success": true,
  "exit_code": 0,
  "detail": null
}
```

Rules:

- Append-only; never truncate from API.
- Redact tokens, keys, and `.env`-style content from any stderr captured in `detail`.
- Do not log request bodies (empty for restart).

## UI Confirmation Flow (5A)

1. User clicks **Restart Gateway** on the Hermes Gateway dashboard card.
2. Modal shows: service name, action description, warning that gateway messaging will briefly interrupt.
3. User clicks **Confirm restart** (optional: type `RESTART`).
4. Browser sends `POST /api/hermes/restart`.
5. UI displays structured result and refreshes gateway status.

## Error Handling Summary

| Condition | HTTP | User-visible detail |
|-----------|------|---------------------|
| Feature disabled | 403 | Write actions disabled |
| Cooldown active | 429 | Try again later |
| launchctl missing | 502 | launchctl unavailable |
| Non-zero exit | 502 | Action failed (truncated, redacted) |
| Timeout (5s) | 504 | Action timed out |
| Unknown action | 404 | Not in allowlist |

## Security Boundaries

- Cannot target any label other than `HERMES_LAUNCHD_LABEL`.
- Cannot pass plist path from client.
- Cannot chain to arbitrary subprocess.
- External access still requires Cloudflare Access login before POST reaches backend.

## Related Documents

- `docs/security/README.md` — gates and audit requirements
- `docs/architecture/deployment.md` — LaunchAgent separation
- `docs/api/bob-interaction.md` — Bob task entry (Track B)
