# Hermes UI for Bob

## What This Is

Hermes UI for Bob is a secure web-based control panel that runs locally on Bob / Mac Mini M4 and listens on `127.0.0.1:8787`. It gives Truls a practical read-only dashboard for Bob, Hermes gateway status, and simple system information, with later external access protected by Cloudflare Tunnel and Cloudflare Access.

The project is driven by the Notion-exported documentation in `docs/notion/`. That documentation is the authoritative project context for scope, architecture, security rules, Bob environment details, and future operational workflows.

## Core Value

Truls can safely see whether Bob and Hermes are healthy without exposing shell access, secrets, or unsafe service controls.

## Requirements

### Validated

(None yet - ship to validate)

### Active

- [ ] Hermes UI runs locally on Bob and binds only to `127.0.0.1:8787`.
- [ ] The first MVP is read-only: status, Hermes status, and system information only.
- [ ] No free terminal or arbitrary command execution is available in the browser.
- [ ] Hermes start, stop, and restart actions are not implemented before `launchctl` commands and log paths are verified.
- [ ] External access is designed for Cloudflare Tunnel and Cloudflare Access, not direct public binding.
- [ ] Real `.env` files are never committed; `.env.example` is the tracked template.

### Out of Scope

- Free browser terminal - too dangerous for a remotely reachable control panel.
- Start, stop, and restart controls in MVP - gated until launchctl commands and log paths are verified on Bob.
- Full agent orchestration - not needed for the first safe operational dashboard.
- Advanced user management - Cloudflare Access is the external access boundary.
- Full historical database - defer until read-only operational value is proven.
- Mobile-optimized app beyond responsive basics - desktop-first dashboard is enough for MVP.
- Direct public exposure - service must not bind to public network interfaces.

## Context

Bob is the new Mac Mini M4 server machine. It is intended to host Hermes/Bob, LM Studio, Docker-based services, Cloudflare Tunnel, local APIs, and internal automations. MacBook Pro is the daily working machine and client.

Known Bob details from `docs/notion/08 Dette trenger Truls å finne frem...`:

- Hostname: `Truls-sin-Mac-mini.local`
- LocalHostName: `Truls-sin-Mac-mini`
- Local IP: `192.168.0.106`
- Bob user: `trulsdahl`
- SSH aliases: `Bob` locally and `BobRemote` via Cloudflare Access
- External SSH host: `bob-ssh.strategistudio.no`
- Hermes install directory: `/Users/trulsdahl/.hermes/hermes-agent`
- Hermes launch agent label: `ai.hermes.gateway`
- LaunchAgent plist: `/Users/trulsdahl/Library/LaunchAgents/ai.hermes.gateway.plist`
- Hermes gateway process observed as Python module: `python -m hermes_cli.main gateway run --replace`

Likely but not yet approved service commands:

- Start: `launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/ai.hermes.gateway.plist`
- Stop: `launchctl bootout gui/$(id -u) ~/Library/LaunchAgents/ai.hermes.gateway.plist`
- Restart: `launchctl kickstart -k gui/$(id -u)/ai.hermes.gateway`
- Status: `launchctl list | grep -i hermes` or `ps aux | grep -i '[h]ermes'`

These commands must be verified against the actual plist and runtime behavior before any write action is wired into the UI.

## Constraints

- **Security**: No free shell, no arbitrary command execution, no secrets in UI output or logs.
- **Network**: Backend listens on `127.0.0.1:8787`; external access goes through Cloudflare Tunnel and Cloudflare Access.
- **MVP Scope**: First release is read-only: status, Hermes status, and system information.
- **Operations**: Start/stop/restart requires verified `launchctl` commands and confirmed log paths first.
- **Secrets**: Real `.env` is local-only and ignored by git; `.env.example` is the committed template.
- **Project Method**: Use original GSD master flow: discuss -> plan -> execute -> verify.
- **Source Context**: `docs/notion/` remains authoritative unless superseded by newer `.planning/` decisions.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Run Hermes UI on Bob, not as a local MacBook app | Bob is the source of truth for Hermes status and local service commands | - Pending |
| Bind only to `127.0.0.1:8787` | Prevent accidental LAN/public exposure; Cloudflare Tunnel handles external access | - Pending |
| Use Cloudflare Access for external protection | Keeps authentication outside MVP app complexity | - Pending |
| First MVP is read-only | Reduces risk while service identity, logs, and launchctl behavior are verified | - Pending |
| Exclude free terminal permanently from MVP | A browser terminal would create unnecessary remote-control risk | - Pending |
| Gate start/stop/restart until verification | Notion docs mark commands as likely, not fully confirmed | - Pending |
| Track `.env.example`, never real `.env` | Keeps configuration discoverable without committing secrets | - Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? -> Move to Out of Scope with reason
2. Requirements validated? -> Move to Validated with phase reference
3. New requirements emerged? -> Add to Active
4. Decisions to log? -> Add to Key Decisions
5. "What This Is" still accurate? -> Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check - still the right priority?
3. Audit Out of Scope - reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-06-03 after initialization*
