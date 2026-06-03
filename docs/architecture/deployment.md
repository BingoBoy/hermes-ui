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

Hermes UI reads gateway status and verified gateway logs through allowlisted backend logic. It does not control the gateway in the current read-only phase.

## Forward Plan: Cloudflare Access and Tunnel

Planning completed in Phase 4. Execution is deferred until manual Cloudflare setup is run on Bob.

| Item | Planned value |
|------|---------------|
| Public URL | `https://hermes.strategistudio.no` |
| Fallback URL | `https://hermes-ui.strategistudio.no` |
| Tunnel name | `mac-mini-m4-tunnel` |
| Ingress target | `http://127.0.0.1:8787` |
| Access policy | `Only Truls` pattern in Zero Trust |

Planned sequence:

1. Keep Hermes UI bound to `127.0.0.1:8787` on Bob.
2. Authenticate `cloudflared` and create or select the Bob Mac Mini M4 tunnel.
3. Route `hermes.strategistudio.no` through the tunnel to loopback.
4. Protect the hostname with Cloudflare Access before sharing the URL.
5. Re-run local and external verification.

See `docs/architecture/cloudflare.md` for command checklist and verification gates.

No Cloudflare configuration was changed during the planning phase.

## Related Documents

- `README.md` — quick Bob operations and API smoke tests
- `docs/security/README.md` — security boundaries and gates
- `docs/architecture/logging.md` — verified Hermes gateway log allowlist
- `docs/architecture/cloudflare.md` — Cloudflare Tunnel and Access plan
