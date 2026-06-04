# Hermes UI for Bob

## What This Is

Hermes UI for Bob is a secure web-based control panel on Bob / Mac Mini M4 (`127.0.0.1:8787`) for operational visibility: health status, bounded gateway logs, allowlisted service actions, Bob kanban task entry, and read-only LaunchAgent operations. External access is via Cloudflare Tunnel and Cloudflare Access at `https://hermes-ui.strategistudio.no`.

Authoritative context: `docs/notion/` and GSD planning in `.planning/`.

## Core Value

Truls can safely see whether Bob and Hermes are healthy without exposing shell access, secrets, or unsafe service controls.

## Current State (2026-06-04)

**Shipped milestones:**

- **v1** — Phases 1–6 (MVP → logs → docs → Cloudflare → UX → restart/Bob APIs → operations)
- **v2.1-bob-ux** — Bob dashboard UX (6A–6N)

**Production:** Bob and `origin/main` at `dd7e661`; 77 pytest passing.

**Next:** `/gsd-new-milestone` for v1.1+ scope, or backlog item (5B, OPS-01, Hermes UI logs).

## Requirements

### Validated

**v1 (phases 1–6):**

- ✓ Read-only MVP — status, system, Hermes APIs — v1 Phase 1
- ✓ Security boundaries — no shell, no secrets in output — v1 Phase 1
- ✓ Bounded gateway logs — v1 Phase 2
- ✓ Bob LaunchAgent deployment documented — v1 Phase 3
- ✓ Cloudflare Tunnel + Access — v1 Phase 4
- ✓ Dashboard UX cleanup — v1 Phase 4.5
- ✓ Gateway restart (allowlisted, audited) — v1 Phase 5A
- ✓ Bob kanban create/list/show — v1 Phase 5C/5D
- ✓ LaunchAgent operations cards — v1 Phase 6 (OPS-02, OPS-03)

**v2.1-bob-ux:**

- ✓ Bob Inbox, templates, results, assignee, artifacts, queue labels — v2.1-bob-ux

### Active (backlog — no milestone file yet)

- [ ] Gateway start/stop after live `bootstrap`/`bootout` verify (5B)
- [ ] Cloudflare tunnel status in UI (OPS-01)
- [ ] Hermes UI LaunchAgent logs in bounded viewer
- [ ] Bob worker environment: `hermes-assignee` available

### Out of Scope

- Free browser terminal
- Arbitrary command execution API
- Direct public binding (use Cloudflare)
- Full agent orchestration in UI
- Mobile-first app beyond responsive basics

## Context

- **Bob:** Mac Mini M4, user `trulsdahl`, Hermes gateway label `ai.hermes.gateway`
- **Hermes UI:** LaunchAgent `no.truls.hermes-ui`, loopback `8787`
- **Write routes:** `POST /api/hermes/restart`, `POST /api/bob/tasks` only

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Bob-hosted UI, loopback bind | Source of truth on server | ✓ v1 |
| Cloudflare Access for external auth | No in-app user management | ✓ v1 Phase 4 |
| Read-first, gated writes | Safety before controls | ✓ v1; restart + Bob tasks shipped |
| No free terminal | Remote-control risk | ✓ Permanent |
| Server-controlled Bob assignee | Client cannot set `--assignee` | ✓ v2.1-bob-ux |
| Docker ops off on Bob until needed | OPS-03 assessed | ✓ v1 Phase 6 |

## Evolution

Updated at milestone boundaries via `/gsd-complete-milestone`.

---
*Last updated: 2026-06-04 after v1 milestone*
