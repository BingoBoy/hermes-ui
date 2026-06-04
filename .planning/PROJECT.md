# Hermes UI for Bob

## What This Is

Hermes UI for Bob is a secure web-based control panel on Bob / Mac Mini M4 (`127.0.0.1:8787`) for operational visibility: health status, bounded gateway logs, allowlisted service actions, Bob kanban task entry, and read-only LaunchAgent operations. External access is via Cloudflare Tunnel and Cloudflare Access at `https://hermes-ui.strategistudio.no`.

Authoritative context: `docs/notion/` and GSD planning in `.planning/`.

## Core Value

Truls can safely see whether Bob and Hermes are healthy without exposing shell access, secrets, or unsafe service controls.

## Current Milestone: v1.1 Operational Visibility

**Goal:** Extend production dashboard with **read-only** Cloudflare tunnel visibility and Hermes UI’s own bounded logs — without new write routes or 5B start/stop.

**Target features:**

- Cloudflare Tunnel / `cloudflared` status card (OPS-01)
- Hermes UI LaunchAgent logs in existing logs viewer (LOG-UI)
- Security regression checks on both phases

**Explicitly not in v1.1:** Gateway start/stop (5B), `hermes-assignee` worker fix (external ops), LM Studio/n8n cards.

## Current State (2026-06-04)

**Shipped milestones:**

- **v1** — Phases 1–6
- **v2.1-bob-ux** — 6A–6N

**Production:** Bob @ `c9ac8bf`; `https://hermes-ui.strategistudio.no`; 77 pytest passing.

**Planning:** v1.1 requirements + roadmap defined — **no implementation started.**

**Next:** `/gsd-discuss-phase 7` then `/gsd-plan-phase 7` (recommended order: Phase 7 → Phase 8).

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

### Active (v1.1 — see `.planning/REQUIREMENTS.md`)

- [ ] OPS-01–03: Cloudflare tunnel status (Phase 7)
- [ ] LOG-UI-01–03: Hermes UI logs in dashboard (Phase 8)
- [ ] SEC-01–02: No regression on write-route allowlist (Phases 7–8)

### Backlog (post–v1.1)

- [ ] Gateway start/stop — 5B, maintenance window + live verify
- [ ] `hermes-assignee` on Bob worker — external ops
- [ ] LM Studio / n8n adjacent services — product decision required

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
*Last updated: 2026-06-04 — milestone v1.1 Operational Visibility started*
