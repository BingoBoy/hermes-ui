# Roadmap: Hermes UI for Bob

**Created:** 2026-06-03  
**Flow:** discuss -> plan -> execute -> verify  
**Current milestone:** v1.1 — Operational Visibility (planning)

## Milestones

- ✅ **v1** — Safe Operations Dashboard (Phases 1–6) — shipped 2026-06-04 → [archive](milestones/v1-ROADMAP.md)
- ✅ **v2.1-bob-ux** — Bob Dashboard / Kanban UX (6A–6N) — shipped 2026-06-04 → [archive](milestones/v2.1-bob-ux-ROADMAP.md)
- 🚧 **v1.1** — Operational Visibility (Phases 7–8) — **planning** 2026-06-04

## Overview (v1.1 active)

| Phase | Name | Goal | Requirements | Risk |
|-------|------|------|--------------|------|
| 7 | Cloudflare Tunnel Status | Read-only tunnel/`cloudflared` visibility in dashboard | OPS-01–03, SEC-* | Low — read-only |
| 8 | Hermes UI Logs Viewer | Bounded Hermes UI LaunchAgent logs in existing logs API/UI | LOG-UI-01–03, SEC-* | Low — extends Phase 2 pattern |

**Deferred (not v1.1 phases):**

| Item | Gate | Notes |
|------|------|-------|
| **5B** Gateway start/stop | Maintenance window + live `bootstrap`/`bootout` verify | v2 — do not plan until gate met |
| **OPS-EXT-01** `hermes-assignee` | Bob Hermes Agent ops | Runbook/docs only; not UI code in v1.1 |
| **OPS-ADJ-01** LM Studio / n8n | Product + Bob verify | Backlog after v1.1 |

## Phase 7: Cloudflare Tunnel Status

**Goal:** Show read-only Cloudflare Tunnel health for the Hermes UI hostname without exposing credentials or widening the attack surface.

**Requirements:** OPS-01, OPS-02, OPS-03, SEC-01, SEC-02

**Depends on:** v1 Phase 4 (tunnel live at `https://hermes-ui.strategistudio.no`), v1 Phase 6 (operations section pattern)

**Status:** Not started — discuss → plan → execute → verify

**Success criteria:**

1. Bob preflight documents safe read-only checks (`cloudflared` version, tunnel list/name, process state) — no secrets in repo.
2. New read-only API (e.g. `GET /api/tunnel` or section under `/api/operations`) returns structured JSON: hostname, tunnel name, connected/running, checked_at, errors safe for UI.
3. Dashboard section (e.g. under «Drift og tjenester» or dedicated card) shows tunnel status in plain language.
4. No new POST routes; no client input for tunnel ID, paths, or tokens.
5. pytest + security greps pass; Bob loopback verify after deploy.

**Suggested plans:**

- Verify on Bob: `which cloudflared`, allowed subcommands, tunnel name `bob-mac-mini-m4` (from Phase 4 docs).
- Implement allowlisted tunnel probe module + API.
- Dashboard card + tests.

**Planning artifacts (to create):**

- `.planning/phases/07-cloudflare-tunnel-status/07-CONTEXT.md` (via `/gsd-discuss-phase 7`)
- `.planning/phases/07-cloudflare-tunnel-status/07-PLAN.md` (via `/gsd-plan-phase 7`)

## Phase 8: Hermes UI Logs Viewer

**Goal:** Add Hermes UI’s own LaunchAgent logs to the bounded, redacted log viewer (today only gateway logs are enabled).

**Requirements:** LOG-UI-01, LOG-UI-02, LOG-UI-03, SEC-01, SEC-02

**Depends on:** v1 Phase 2 (logs allowlist + redaction), Phase 7 optional ordering (can run parallel after discuss)

**Status:** Not started

**Success criteria:**

1. Log paths verified on Bob: `~/.hermes-ui/logs/hermes-ui.log`, `hermes-ui.error.log` (from plist / operations API).
2. `log_sources.py` allowlist extended with `hermes_ui_stdout` / `hermes_ui_stderr` (or equivalent IDs), `enabled=True` after verify.
3. Dashboard logs section lists new sources; same line limits (50/100/500) and redaction rules as gateway.
4. No path parameters from client; no write routes.
5. pytest + Bob curl verify.

**Suggested plans:**

- Verify paths and redaction on Bob.
- Extend allowlist + API metadata + dashboard source selector.
- Tests and deploy verify.

**Planning artifacts (to create):**

- `.planning/phases/08-hermes-ui-logs-viewer/08-CONTEXT.md`
- `.planning/phases/08-hermes-ui-logs-viewer/08-PLAN.md`

---

<details>
<summary>✅ v1 — Safe Operations Dashboard (Phases 1–6) — SHIPPED 2026-06-04</summary>

[Full archive](milestones/v1-ROADMAP.md)

</details>

<details>
<summary>✅ v2.1-bob-ux — Bob Dashboard / Kanban UX (6A–6N) — SHIPPED 2026-06-04</summary>

[Full archive](milestones/v2.1-bob-ux-ROADMAP.md)

</details>

## Backlog (post–v1.1)

| Item | Notes |
|------|--------|
| **5B** Gateway start/stop | Blocked until maintenance-window live verify |
| **OPS-EXT-01** `hermes-assignee` on Bob worker | External Hermes Agent |
| **OPS-ADJ-01** LM Studio / n8n / Docker adjacent | Needs Bob product verify |

---
*Roadmap updated: 2026-06-04 — milestone v1.1 started*
