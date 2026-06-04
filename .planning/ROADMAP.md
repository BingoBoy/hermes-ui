# Roadmap: Hermes UI for Bob

**Created:** 2026-06-03
**Granularity:** Standard
**Flow:** discuss -> plan -> execute -> verify

## Milestones

- **v2.1-bob-ux** — Bob Dashboard / Kanban UX (6A–6N) — shipped 2026-06-04 → [archive](milestones/v2.1-bob-ux-ROADMAP.md)
- **Phase 6** — Operations Enrichment — shipped 2026-06-04
- **Phase 5** — Service actions + Bob tasks — complete on Bob (5B deferred)
- **Next:** Audit or choose from [Backlog](#backlog--not-yet-planned) — no active phase

## Overview

| Phase | Name | Goal | Requirements | UI hint |
|-------|------|------|--------------|---------|
| 1 | Read-Only MVP Foundation | Deliver the first safe local MVP: context lock, read-only backend, status dashboard, and built-in verification | PROJ-01, PROJ-02, PROJ-03, RUN-01, RUN-02, RUN-03, RUN-04, API-01, API-02, API-03, API-04, UI-01, UI-02, UI-03, UI-04, SEC-01, SEC-02, SEC-03, SEC-04 | yes |
| 2 | Verified Logs Viewer | Add bounded Hermes log display only after actual log paths and redaction rules are verified | LOGS-01, LOGS-02, LOGS-03 | yes |
| 3 | Document Bob LaunchAgent Deployment | Document verified Hermes UI LaunchAgent operations on Bob without changing runtime code | RUN-01, RUN-02, OPS-02 | no |
| 4 | Cloudflare Access and Tunnel | Expose Hermes UI safely through Cloudflare Tunnel and Cloudflare Access | OPS-01, SEC-04 | yes |
| 4.5 | Dashboard UX Cleanup | Improve read-only dashboard usability without changing backend security model | UI-01, UI-02, UI-03, UI-04 | yes |
| 5 | Verified Service Actions and Bob Interaction | Plan and deliver safe gateway controls and bounded Bob task entry after command verification | ACT-01, ACT-02, ACT-03, ACT-04 | yes |
| 6 | Operations Enrichment | Add richer operational views for launchctl, Docker, and adjacent services where relevant | OPS-02, OPS-03 | yes |

## Phase 1: Read-Only MVP Foundation

**Goal:** Deliver the first safe local MVP: context lock, read-only backend, status dashboard, and built-in verification.

**Requirements:** PROJ-01, PROJ-02, PROJ-03, RUN-01, RUN-02, RUN-03, RUN-04, API-01, API-02, API-03, API-04, UI-01, UI-02, UI-03, UI-04, SEC-01, SEC-02, SEC-03, SEC-04

**Success criteria:**
1. `docs/notion/` is referenced as authoritative source context in planning docs.
2. MVP boundaries are explicit: read-only first, no free terminal, no arbitrary command execution.
3. Start/stop/restart are documented as gated until `launchctl` commands and log paths are verified.
4. Backend starts on `127.0.0.1:8787` by default.
5. `GET /api/status`, `GET /api/system`, and `GET /api/hermes/status` return structured JSON and fail safely.
6. Dashboard shows service, Bob/system, and Hermes read-only status.
7. No start, stop, restart, log-view, free-terminal, or user-defined shell endpoints exist.
8. README and `docs/security/README.md` describe local run instructions and security boundaries.
9. Verification confirms `.env` is not committed and `ALLOW_UNSAFE_COMMANDS=false`.

**Suggested plans:**
- Lock context, state, and safety rules.
- Implement read-only FastAPI MVP.
- Verify endpoints, local binding, and security boundaries.

## Phase 2: Verified Logs Viewer

**Goal:** Prepare the bounded Hermes log viewer by verifying actual log paths, defining the server-side allowlist, and locking redaction rules before implementation.

**Requirements:** LOGS-01, LOGS-02, LOGS-03

**Success criteria:**
1. Actual Hermes log path is verified on Bob.
2. Log output is bounded by a safe line limit.
3. Log output is sanitized before display.
4. No raw environment or credential output is exposed.
5. No production log viewer code or logs API route is implemented during phase discussion/planning.
6. Future log viewer reads only server-side allowlisted sources by `log_id`, never paths from client input.

**Suggested plans:**
- Verify LaunchAgent log paths and candidate Hermes log files.
- Define allowlist and redaction contracts.
- Plan bounded read-only log endpoint and UI panel for a later execution step.

## Phase 3: Document Bob LaunchAgent Deployment

**Goal:** Document that Hermes UI runs as a verified LaunchAgent on Bob without changing runtime code.

**Requirements:** RUN-01, RUN-02, OPS-02

**Success criteria:**
1. README documents Bob LaunchAgent start, stop, restart, status, log paths, and local API checks.
2. `docs/architecture/deployment.md` documents local binding, launchd setup, log paths, and forward Cloudflare plan.
3. GSD state records verified Bob LaunchAgent metadata.
4. No backend code, secrets, or Cloudflare credentials are added.

**Suggested plans:**
- Verify LaunchAgent metadata on Bob.
- Write deployment and operations documentation.
- Update GSD state and re-run docs-only verification.

## Phase 4: Cloudflare Access and Tunnel

**Goal:** Expose Hermes UI safely through Cloudflare Tunnel and Cloudflare Access while keeping local binding on `127.0.0.1:8787`.

**Requirements:** OPS-01, SEC-04

**Status:** Complete on 2026-06-04

**Success criteria:**
1. Tunnel identity and hostname are verified before configuration.
2. Hermes UI remains bound to loopback on Bob.
3. External access is protected by Cloudflare Access.
4. No Cloudflare credentials are committed to the repo.
5. Planning docs include manual command checklist and verification gates.

**Actual outcome:**
- Public URL: `https://hermes-ui.strategistudio.no`
- Tunnel: `bob-mac-mini-m4` (existing tunnel reused)
- Route: Published application route to `http://127.0.0.1:8787`
- Access: self-hosted application with `Only Truls` policy
- Unauthenticated curl verified with HTTP `302` redirect

## Phase 4.5: Dashboard UX Cleanup

**Goal:** Improve the read-only dashboard for daily use without changing backend security boundaries.

**Requirements:** UI-01, UI-02, UI-03, UI-04

**Status:** Complete on 2026-06-04

**Success criteria:**
1. Status cards show readable labels instead of raw JSON.
2. Gateway logs render as scrollable readable lists.
3. Technical JSON remains available in collapsible sections.
4. Manual refresh is available.
5. No write routes or backend security changes are introduced.

## Phase 5: Verified Service Actions and Bob Interaction

**Goal:** Plan and deliver safe gateway service controls and a bounded Bob task entry point without browser terminal or arbitrary command execution.

**Requirements:** ACT-01, ACT-02, ACT-03, ACT-04 (Track A); Bob task entry (Track B)

**Status:** **Complete on Bob** (2026-06-04) — restart, Bob tasks, and list/show live in production; 5B deferred

**Bob production (resolved — formerly «deploy pending»):**

- `ALLOW_SERVICE_ACTIONS=true` — restart gateway via dashboard/API live
- `ALLOW_BOB_TASKS=true`, `HERMES_BOB_TASK_ASSIGNEE=default` — create/list/show live
- Verified on Bob loopback and via `https://hermes-ui.strategistudio.no` (Cloudflare Access)

**Sub-phases:**

| ID | Name | Goal | Status |
|----|------|------|--------|
| 5A | Restart-only action | POST restart with audit, confirmation, feature gate | **Complete** — live on Bob |
| 5B | Start/stop actions | bootstrap/bootout after live verification | **Blocked** — not live-verified; maintenance window required |
| 5C | Bob task entry | kanban create wrapper API | **Complete** — live on Bob |
| 5D | Response/history view | Read-only kanban list/show | **Complete** — live on Bob |

**Success criteria:**
1. Exact launchctl restart command verified on Bob (`kickstart -k`).
2. Write actions use fixed argv, no shell, no client command input.
3. Write actions require explicit UI confirmation and append-only audit log.
4. Bob task entry uses allowlisted Hermes CLI (kanban create), not free chat/terminal.
5. Failed actions return safe structured JSON errors.

**Verified commands (Bob, 2026-06-04):**
- Restart: `launchctl kickstart -k gui/$(id -u)/ai.hermes.gateway` — live verified
- Start/stop: documented, require maintenance-window verification before 5B

**Suggested plans:**
- 5A: Allowlisted runner + audit + POST restart + confirmation UX
- 5B: Start/stop endpoints after bootstrap/bootout verification
- 5C: POST `/api/bob/tasks` via `hermes kanban create`
- 5D: Read-only task history endpoints

**Planning artifacts:**
- `.planning/phases/05-verified-service-actions/05-CONTEXT.md`
- `.planning/phases/05-verified-service-actions/05-PLAN.md`
- `.planning/phases/05C-bob-task-entry/05C-CONTEXT.md`
- `.planning/phases/05C-bob-task-entry/05C-PLAN.md`
- `docs/api/service-actions.md`
- `docs/api/bob-interaction.md`

<details>
<summary>✅ v2.1-bob-ux — Bob Dashboard / Kanban UX (Phases 6A–6N) — SHIPPED 2026-06-04</summary>

Full phase details: [milestones/v2.1-bob-ux-ROADMAP.md](milestones/v2.1-bob-ux-ROADMAP.md)

- [x] 6A–6B: Task follow-up + Bob Inbox
- [x] 6C–6D: Task templates + optional inputs
- [x] 6E–6I: Result actions + assignee + summary + UAT closure
- [x] 6J–6M: Layout, expand UAT, artifacts, queue hygiene
- [x] 6N: Milestone documentation cleanup

Production-verified on Bob. Audit: [milestones/v2.1-bob-ux-MILESTONE-AUDIT.md](milestones/v2.1-bob-ux-MILESTONE-AUDIT.md)

</details>

## Phase 6: Operations Enrichment

**Goal:** Add richer operational views for launchctl, Docker, and adjacent services where relevant.

**Status:** **Shipped** 2026-06-04 — verified (pytest 77, Bob `/api/operations`, UAT passed)

**Requirements:** OPS-02, OPS-03

**Note:** Distinct from decimal phases 6A–6M (Bob Dashboard / Kanban UX), which are complete.

**Delivered:**

- `GET /api/operations` — read-only LaunchAgent metadata (Hermes UI + gateway)
- Dashboard **«Drift og tjenester»** after Bob blocks
- Docker off by default (`HERMES_OPS_INCLUDE_DOCKER=false` on Bob)

**Planning artifacts:**

- `.planning/phases/06-operations-enrichment/06-CONTEXT.md`
- `.planning/phases/06-operations-enrichment/06-RESEARCH.md`
- `.planning/phases/06-operations-enrichment/06-PLAN.md`
- `.planning/phases/06-operations-enrichment/06-VERIFICATION.md`
- `.planning/phases/06-operations-enrichment/06-UAT.md`

**Git range:** `01d04f8` (plan) → `8632f49` (feat) → `47d8276` (verify docs)

**Success criteria:**
1. LaunchAgent detail display uses verified label/plist values.
2. Docker status is added only if Docker becomes relevant to Hermes or adjacent services.
3. Operational cards remain read-only unless a verified write-action phase approves controls.

**Suggested plans:**
- Verify operational sources.
- Add read-only operational status cards.
- Re-run security boundary checks.

## Backlog / not yet planned

Items **not** in the shipped roadmap phases 1–6. Do not duplicate work already delivered:

| Item | Notes |
|------|--------|
| **5B** Gateway start/stop | `bootstrap`/`bootout` documented; **blocked** until live verify in maintenance window |
| **OPS-01** Cloudflare tunnel status in UI | Tunnel/Access documented (Phase 4); no live tunnel status card yet |
| **Hermes UI LaunchAgent logs in dashboard** | Paths at `~/.hermes-ui/logs/`; not in bounded logs allowlist (gateway logs only today) |
| **LM Studio / n8n** adjacent services | Mentioned in Notion only; no plan |
| **Project requirements traceability** | `REQUIREMENTS.md` v1 checkboxes not fully synced — defer to `/gsd-audit-milestone` or project audit |

**Already delivered (remove from «future» thinking):**

- Bounded gateway logs viewer — Phase 2
- Gateway restart + audit — Phase 5A on Bob
- Bob kanban create/list/show — Phase 5C/5D on Bob (+ v2.1-bob-ux dashboard)
- LaunchAgent operational cards — Phase 6 (`GET /api/operations`)

## Coverage Validation

| Requirement Group | Count | Covered |
|-------------------|-------|---------|
| Project Grounding | 3 | 3 |
| Runtime | 4 | 4 |
| Read-Only API | 4 | 4 |
| Dashboard | 4 | 4 |
| Security | 4 | 4 |

All 19 v1 requirements are mapped to Phase 1 for the first safe read-only MVP. Full checkbox migration to `PROJECT.md` Validated is **deferred** to a future project audit (not updated in this sync).

---
*Roadmap created: 2026-06-03 · v2.1-bob-ux archived: 2026-06-04 · Phase 5–6 Bob production sync: 2026-06-04*
