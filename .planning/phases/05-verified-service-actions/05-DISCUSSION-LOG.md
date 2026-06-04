# Phase 5: Verified Service Actions and Bob Interaction Planning - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in `05-CONTEXT.md`.

**Date:** 2026-06-04
**Phase:** 5-Verified Service Actions and Bob Interaction Planning
**Areas discussed:** Service action commands, security model, Bob interaction entry points, sub-phase breakdown

---

## Track A — Service Action Mechanism

| Option | Description | Selected |
|--------|-------------|----------|
| Direct `launchctl` with fixed argv | Hermes UI runs allowlisted launchctl commands, same as status inspection pattern | ✓ |
| `hermes gateway restart/start/stop` | Delegate to Hermes CLI service management | |
| Shell script wrapper | External script called by backend | |

**User's choice:** Direct fixed `launchctl` only — no shell, no user input, no `hermes gateway --all`.
**Notes:** `launchctl kickstart -k gui/501/ai.hermes.gateway` live-verified on Bob during planning (PID 88059 → 53383). Start/stop commands documented but not live-tested to avoid unnecessary downtime.

---

## Track A — First Write Action Scope

| Option | Description | Selected |
|--------|-------------|----------|
| Restart-only (5A) | Single POST endpoint, lowest risk | ✓ |
| Start + stop + restart together | Full ACT-01..03 in one execute phase | |
| Read-only planning only | No execute until all three verified | |

**User's choice:** Sub-phase 5A restart-only first; 5B adds start/stop after bootstrap/bootout verification.

---

## Track A — Confirmation UX

| Option | Description | Selected |
|--------|-------------|----------|
| Modal + confirm button | Show action summary, require explicit click | ✓ |
| Typed confirmation token | User types `RESTART` before submit | Optional for 5A |
| Double confirm with countdown | Delay + second click | |

**User's choice:** Explicit confirmation required before any POST. Typed token left to planner discretion.

---

## Track B — Bob Task Entry Mechanism

| Option | Description | Selected |
|--------|-------------|----------|
| `hermes kanban create` | Durable task queue, async, idempotency, bounded title/body | ✓ (primary for 5C) |
| `hermes chat -q ... -Q` | Synchronous single query | Secondary / higher risk |
| Telegram gateway direct | Bypass Hermes UI, use existing channel | |
| New HTTP endpoint in gateway | Would require Hermes upstream changes | |
| Browser chat / terminal | Full interactive shell or chat | Rejected |

**User's choice:** Kanban create as primary Bob entry; chat -q as optional sync path after strict caps. No chat UI or terminal in scope.

**Notes:** SSH inspection on Bob found:
- No Hermes gateway HTTP listen port
- `hermes send` is outbound-only (Telegram/Discord/etc.)
- `hermes kanban` has full task lifecycle (create, list, show, dispatch)
- Gateway handles inbound Telegram; not suitable as UI ingress without allowlist

---

## Track B — Response Retrieval

| Option | Description | Selected |
|--------|-------------|----------|
| Read-only kanban list/show | Poll task status and comments via CLI | ✓ (5D) |
| `hermes sessions list` | Session history for completed queries | ✓ (5D supplement) |
| WebSocket streaming | Real-time agent output in UI | Deferred |

---

## Claude's Discretion

- Audit log format (JSONL recommended)
- Restart cooldown interval (30s recommended)
- Whether typed `RESTART` is mandatory in 5A UI

---

## Deferred Ideas

- Full chat interface
- `hermes -z` oneshot with tool auto-approval
- Controlling non-gateway LaunchAgents from UI
- Cloudflare or LaunchAgent changes during Phase 5
