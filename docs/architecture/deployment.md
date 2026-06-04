# Deployment Architecture: Hermes UI on Bob

## Purpose

This document describes how Hermes UI is deployed on Bob as a local LaunchAgent. It is operational documentation only — no Cloudflare or write-action configuration is implemented here.

## Verified Deployment on Bob

Inspected read-only on Bob (`Truls-sin-Mac-mini.local`) on 2026-06-03.

| Field | Verified value |
|-------|----------------|
| Hostname | `Truls-sin-Mac-mini.local` |
| User | `trulsdahl` |
| LaunchAgent label | `no.truls.hermes-ui` |
| LaunchAgent plist | `/Users/trulsdahl/Library/LaunchAgents/no.truls.hermes-ui.plist` |
| WorkingDirectory | `/Users/trulsdahl/Dev/hermes-ui` |
| Program | `/Users/trulsdahl/Dev/hermes-ui/.venv/bin/uvicorn backend.main:app --host 127.0.0.1 --port 8787` |
| StandardOutPath | `/Users/trulsdahl/.hermes-ui/logs/hermes-ui.log` |
| StandardErrorPath | `/Users/trulsdahl/.hermes-ui/logs/hermes-ui.error.log` |
| Bind address | `127.0.0.1:8787` |
| API status | `ok` |
| `read_only` | `true` |
| `allow_unsafe_commands` | `false` |

## Local Binding

Hermes UI listens only on the loopback interface:

```text
127.0.0.1:8787
```

Rules:

- Do not bind to `0.0.0.0` or a LAN-facing address.
- External access must go through Cloudflare Tunnel and Cloudflare Access in a later phase.
- The LaunchAgent plist sets `HERMES_UI_HOST=127.0.0.1` and `HERMES_UI_PORT=8787`.

## launchd / LaunchAgent Model

Hermes UI runs under the user LaunchAgent domain on Bob:

```text
gui/$(id -u)/no.truls.hermes-ui
```

Operational commands:

```bash
# Load and start
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/no.truls.hermes-ui.plist

# Stop and unload
launchctl bootout gui/$(id -u) ~/Library/LaunchAgents/no.truls.hermes-ui.plist

# Restart in place
launchctl kickstart -k gui/$(id -u)/no.truls.hermes-ui

# Inspect loaded job
launchctl list | grep hermes-ui
```

Status checks:

```bash
lsof -nP -iTCP:8787 -sTCP:LISTEN
curl -s http://127.0.0.1:8787/api/status
```

## Hermes UI Log Paths

| Stream | Path |
|--------|------|
| stdout | `/Users/trulsdahl/.hermes-ui/logs/hermes-ui.log` |
| stderr | `/Users/trulsdahl/.hermes-ui/logs/hermes-ui.error.log` |

These are LaunchAgent-managed files. They are not yet exposed through the bounded logs API allowlist. Treat them as operational logs, not as a browser-facing log source until redaction and allowlist review are complete.

## Environment and Secrets

The LaunchAgent sets safe runtime defaults:

```text
HERMES_UI_ENV=production
HERMES_UI_HOST=127.0.0.1
HERMES_UI_PORT=8787
ALLOW_UNSAFE_COMMANDS=false
```

Rules:

- Real `.env` files stay local and uncommitted.
- `.env.example` remains the tracked template.
- Do not store API keys, tokens, passwords, private keys, or Cloudflare credentials in the plist or repo.

## Relationship to Hermes Gateway

Hermes UI and the Hermes gateway are separate LaunchAgents:

| Service | Label | Port / role |
|---------|-------|-------------|
| Hermes UI | `no.truls.hermes-ui` | `127.0.0.1:8787` dashboard/API |
| Hermes gateway | `ai.hermes.gateway` | gateway process via `hermes_cli` |

Hermes UI reads gateway status and verified gateway logs through allowlisted backend logic. Phase 5A adds restart-only control when `ALLOW_SERVICE_ACTIONS=true`.

### Hermes Gateway LaunchAgent (verified metadata)

| Field | Value |
|-------|-------|
| Label | `ai.hermes.gateway` |
| Plist | `/Users/trulsdahl/Library/LaunchAgents/ai.hermes.gateway.plist` |
| Domain path | `gui/$(id -u)/ai.hermes.gateway` |
| Program | `/Users/trulsdahl/.hermes/hermes-agent/venv/bin/python -m hermes_cli.main gateway run --replace` |
| Stdout log | `/Users/trulsdahl/.hermes/logs/gateway.log` |
| Stderr log | `/Users/trulsdahl/.hermes/logs/gateway.error.log` |

### Service actions (Phase 5A — restart implemented)

When `ALLOW_SERVICE_ACTIONS=true` on Bob:

```bash
# Restart (implemented in UI/API — live verified 2026-06-04)
launchctl kickstart -k gui/$(id -u)/ai.hermes.gateway

# Start (verify in maintenance window before 5B)
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/ai.hermes.gateway.plist

# Stop (verify in maintenance window before 5B)
launchctl bootout gui/$(id -u) ~/Library/LaunchAgents/ai.hermes.gateway.plist

# Detail status
launchctl print gui/$(id -u)/ai.hermes.gateway
```

Rules:

- Hermes UI backend runs these as fixed argv only — no shell, no client input.
- Hermes UI LaunchAgent must not be restartable from the dashboard.
- Do not use `hermes gateway restart --all` from the UI backend.

See `docs/api/service-actions.md` for API and audit contract.

### Bob task entry (Phase 5C)

Hermes UI submits async tasks via the Hermes CLI kanban board (not gateway HTTP, not chat):

| Item | Value |
|------|-------|
| Hermes CLI on Bob | `/Users/trulsdahl/.hermes/hermes-agent/venv/bin/hermes` |
| Create command | `hermes kanban create <title> --body <body> --assignee <server-profile> --idempotency-key <uuid> --json` when `HERMES_BOB_TASK_ASSIGNEE` is set |
| Feature gate | `ALLOW_BOB_TASKS=false` (default) |
| Audit log | `/Users/trulsdahl/.hermes-ui/logs/bob-interactions.log` |
| API | `POST /api/bob/tasks` |

LaunchAgent env (enable only after Bob kanban verify):

```text
ALLOW_BOB_TASKS=false
HERMES_CLI_BIN=/Users/trulsdahl/.hermes/hermes-agent/venv/bin/hermes
HERMES_UI_BOB_AUDIT_LOG=/Users/trulsdahl/.hermes-ui/logs/bob-interactions.log
HERMES_BOB_TASK_ASSIGNEE=default
```

Rules:

- Same subprocess discipline as service actions: fixed argv, no shell, no client flags.
- Bob task assignee is server-controlled. Do not accept assignee from the browser payload.
- `HERMES_BOB_TASK_ASSIGNEE` must be a simple Hermes profile string (`A-Z`, `a-z`, `0-9`, `_`, `-`, `.`). Bob production should use `default` while that is the only spawnable profile.
- After changing LaunchAgent `EnvironmentVariables`, unload and load the job so launchd re-reads the plist; `kickstart` alone may restart with the old environment.
- Enable `ALLOW_BOB_TASKS=true` only after Bob kanban JSON contract is live-verified.
- Kanban dispatcher runs in the gateway process — gateway must stay running.

See `docs/api/bob-interaction.md` and `.planning/phases/05C-bob-task-entry/05C-PLAN.md`.

## Cloudflare Access and Tunnel

Configured in Phase 4 on 2026-06-04.

| Item | Actual value |
|------|--------------|
| Public URL | `https://hermes-ui.strategistudio.no` |
| Tunnel name | `bob-mac-mini-m4` |
| Route type | Published application route |
| Service target | `http://127.0.0.1:8787` |
| Access policy | `Only Truls` pattern |
| Local bind on Bob | `127.0.0.1:8787` unchanged |
| Local `config.yml` | Not created |
| New tunnel created | No |

External access flow:

1. Client hits `https://hermes-ui.strategistudio.no`
2. Cloudflare Access enforces login for unauthenticated requests
3. Cloudflare Tunnel forwards authorized traffic to `http://127.0.0.1:8787`
4. Hermes UI backend remains read-only and loopback-bound

Unauthenticated verification:

```bash
curl -sS -D - -o /dev/null https://hermes-ui.strategistudio.no/api/status
```

Expected: HTTP `302` redirect to Cloudflare Access login, not direct API JSON.

See `docs/architecture/cloudflare.md` for full deployment details.

## Related Documents

- `README.md` — quick Bob operations and API smoke tests
- `docs/security/README.md` — security boundaries and gates
- `docs/architecture/logging.md` — verified Hermes gateway log allowlist
- `docs/api/service-actions.md` — planned gateway write actions
- `docs/api/bob-interaction.md` — planned Bob task entry
