# Security Notes: Hermes UI for Bob

## Phase 1 Boundary

The first MVP is strictly read-only. It may show:

- Hermes UI service status
- Bob / Mac Mini M4 system information
- Hermes gateway status

It must not perform service control actions.

## Explicitly Not Implemented

The following capabilities are intentionally outside Phase 1:

- Start Hermes
- Stop Hermes
- Restart Hermes
- Log viewing
- Free terminal access in the browser
- Arbitrary shell command endpoints
- User-defined command execution
- Direct Cloudflare configuration
- Docker setup

## Network Boundary

Hermes UI defaults to:

```text
127.0.0.1:8787
```

Do not bind the service to `0.0.0.0` for the MVP. Later external access should go through Cloudflare Tunnel and Cloudflare Access.

## Environment and Secrets

`.env.example` is the tracked template. Real `.env` files must stay local and uncommitted.

Never commit or display:

- API keys
- Tokens
- Passwords
- Private SSH keys
- Cloudflare credentials
- Real `.env` contents

`ALLOW_UNSAFE_COMMANDS` must remain `false`.

## Read-Only Inspection

The backend may use fixed local inspection commands for status, such as process or launchctl checks. These commands must not be built from browser input or user-provided API parameters.

If Hermes cannot be checked, the API should return a safe status payload instead of failing open or exposing raw sensitive output.

## Gates Before Future Write Actions

Before adding start, stop, or restart:

1. Verify the exact `launchctl` commands on Bob.
2. Verify the LaunchAgent label and plist path.
3. Add explicit confirmation UX.
4. Add audit logging.
5. Keep actions allowlisted and fixed to Hermes Gateway (`ai.hermes.gateway`) only.
6. Gate with `ALLOW_SERVICE_ACTIONS=false` by default.
7. Re-run security verification.

**Phase 5A execute status (2026-06-04):**

| Action | Command | Implemented |
|--------|---------|-------------|
| Restart | `launchctl kickstart -k gui/$(id -u)/ai.hermes.gateway` | Yes — POST `/api/hermes/restart` |
| Start | `launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/ai.hermes.gateway.plist` | No — Phase 5B |
| Stop | `launchctl bootout gui/$(id -u) ~/Library/LaunchAgents/ai.hermes.gateway.plist` | No — Phase 5B |

Implementation rules:

- Use `subprocess.run` with fixed argv — never `shell=True`.
- Never accept command strings, plist paths, or labels from the client.
- Never control `no.truls.hermes-ui` from the web UI.
- Audit log: `/Users/trulsdahl/.hermes-ui/logs/service-actions.log` (JSONL).
- See `docs/api/service-actions.md` for API contract.

## Bob Task Entry (Phase 5C)

**Status:** Implemented 2026-06-04 — disabled by default (`ALLOW_BOB_TASKS=false`).

| Control | Rule |
|---------|------|
| Feature gate | `ALLOW_BOB_TASKS=false` by default (independent of `ALLOW_SERVICE_ACTIONS`) |
| Allowlisted action | `create_kanban_task` only |
| CLI entry | Fixed argv: `hermes kanban create <title> [--body <body>] --idempotency-key <server-uuid> --json` |
| Subprocess | `subprocess.run(..., shell=False)` — never `shell=True` |
| Client input | `title` + `body` only — no CLI flags, paths, or shell commands |
| Input limits | Title max 200 chars, no newlines; body max 4000 chars |
| Idempotency | Server-generated UUID per submit — not from client |
| Cooldown | 60s between successful creates |
| Audit | `/Users/trulsdahl/.hermes-ui/logs/bob-interactions.log` (JSONL); log `title_hash` + `body_length`, not full body |
| Rejected | `hermes -z`, `hermes chat`, browser terminal, `hermes send`, arbitrary CLI flags |

**API:** `POST /api/bob/tasks` → 403 when gate off, 400 invalid input, 429 cooldown, 202 on success.

**Bob verification gate:** Re-run kanban create/list/show on Bob before enabling `ALLOW_BOB_TASKS=true`. See `docs/api/bob-interaction.md`.

**Read-only (5D):** `GET /api/bob/tasks`, `GET /api/bob/tasks/{task_id}` — same `ALLOW_BOB_TASKS` gate; fixed `kanban list/show --json` argv; strict `task_id` validation; no audit by default.

**Dashboard (6A–6B):** Bob Inbox and auto-refresh are client-side only — no new backend routes or CLI argv.

Before adding logs:

1. Verify actual log paths.
2. Define redaction rules.
3. Bound the number of returned lines.
4. Ensure no secrets are exposed.

## Verified Log Source Gate

Log viewing must use a server-side allowlist. The browser may request a known `log_id`, but it must never provide:

- absolute file paths
- relative file paths
- glob patterns
- directory names
- arbitrary filenames

Verified initial log paths from the Hermes LaunchAgent on Bob:

| Source | Path | Status |
|--------|------|--------|
| Hermes gateway stdout | `/Users/trulsdahl/.hermes/logs/gateway.log` | verified |
| Hermes gateway stderr | `/Users/trulsdahl/.hermes/logs/gateway.error.log` | verified |

Candidate sources that require explicit review before enabling:

| Source | Path | Status |
|--------|------|--------|
| Hermes agent log | `/Users/trulsdahl/.hermes/logs/agent.log` | candidate |
| Hermes errors log | `/Users/trulsdahl/.hermes/logs/errors.log` | candidate |
| Hermes UI backend log | TBD | tbd |

## Log Redaction Rules

Every log line must pass redaction before it is returned by an API or rendered in the UI.

Redact at minimum:

- Bearer headers and bearer tokens
- API keys
- generic tokens
- password fields
- private key blocks
- Cloudflare credentials
- `.env`-style lines
- common secret assignments such as `SECRET=...`, `TOKEN=...`, `PASSWORD=...`, `API_KEY=...`

Suggested replacement:

```text
[REDACTED]
```

Fail closed when uncertain:

- If a line appears to contain a private key block, suppress the line.
- If a multiline secret begins, suppress until the block ends.
- If a log file cannot be read safely, return a structured safe error instead of raw exception text.
- If a requested `source_id` is unknown, return `404` or a safe `unknown_log_source` error.

## Implemented Logs API

Read-only log endpoints are now available:

```text
GET /api/logs/sources
GET /api/logs/{source_id}?lines=100
```

They remain bounded, allowlisted, and redacted. They do not accept file paths from the client.

The redaction layer must run before JSON serialization and before any dashboard rendering.

## Cloudflare Exposure Gate

Hermes UI is exposed externally through Cloudflare Tunnel and Cloudflare Access.

Verified deployment:

| Item | Actual value |
|------|--------------|
| Public hostname | `https://hermes-ui.strategistudio.no` |
| Tunnel name | `bob-mac-mini-m4` |
| Route type | Published application route |
| Service target | `http://127.0.0.1:8787` |
| Access policy | `Only Truls` pattern |
| Unauthenticated curl | HTTP `302` to Cloudflare Access login |

Rules:

- Hermes UI must remain bound to `127.0.0.1:8787` on Bob.
- The tunnel route must target `http://127.0.0.1:8787` only.
- Cloudflare Access must remain active in front of the public URL.
- Do not bind Hermes UI to `0.0.0.0`.
- Do not open router ports for Hermes UI.
- Do not commit Cloudflare credential JSON, Access tokens, or real `.env` values.

Verification:

```bash
curl -sS -D - -o /dev/null https://hermes-ui.strategistudio.no/api/status
```

Expected: redirect to Cloudflare Access, not direct Hermes UI JSON.

See `docs/architecture/cloudflare.md` for deployment details.

