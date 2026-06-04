# Roadmap: Hermes UI for Bob

**Created:** 2026-06-03
**Granularity:** Standard
**Flow:** discuss -> plan -> execute -> verify

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

**Status:** 5A execute complete locally on 2026-06-04 — Bob deploy verification pending

**Sub-phases:**

| ID | Name | Goal | Status |
|----|------|------|--------|
| 5A | Restart-only action | POST restart with audit, confirmation, feature gate | Complete locally — Bob deploy pending |
| 5B | Start/stop actions | bootstrap/bootout after live verification | Blocked |
| 5C | Bob task entry | kanban create wrapper API | **Complete locally** — Bob deploy + ALLOW_BOB_TASKS verify pending |
| 5D | Response/history view | Read-only kanban list/show | **Complete locally** — Bob deploy pending |

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

## Phase 6A–6B: Task Follow-up and Bob Inbox

**Goal:** Improve dashboard UX for Bob task follow-up and a read-only Bob Inbox.

**Status:** Complete — dashboard-only, no new API routes

**Delivered:**

- Bob-oppgaver: status badges, timestamps, auto-refresh, result panel
- Bob Inbox: curated completed/failed/result tasks (client-side)

## Phase 6C: Task Templates

**Goal:** One-click predefined Bob task templates via existing `POST /api/bob/tasks`.

**Status:** Complete — verified 2026-06-04 (automated + user UAT on strategistudio.no)

**Scope:**

- Frontend-only in `backend/dashboard.py`
- Five hardcoded templates (morgenbrief, ukesrapport, konkurrentanalyse, nettside, markedsføring)
- No new backend routes or CLI changes

**Artifacts:** `.planning/phases/06C-task-templates/06C-CONTEXT.md`

## Phase 6D: Template Inputs

**Goal:** Optional input fields on Bob task templates; values merge into task `body` before existing `POST /api/bob/tasks`.

**Status:** Complete — verified 2026-06-04 (automated + Bob deploy + user UAT on strategistudio.no)

**Scope:**

- Frontend-only in `backend/dashboard.py`
- Per-template optional fields + «Send mal til Bob»
- No new backend routes

**Artifacts:** `.planning/phases/06D-template-inputs/06D-CONTEXT.md`

## Phase 6E: Task Result Actions

**Goal:** Safe browser-only copy/expand for Bob Inbox and task detail results.

**Status:** Complete — verified 2026-06-04 (automated); UAT closed via Phase 6I (`t_7b978d4f`)

**Scope:** Frontend-only in `backend/dashboard.py`; Clipboard API + expand; no write routes

**Artifacts:** `.planning/phases/06E-task-result-actions/06E-CONTEXT.md`

## Phase 6F: Bob Kanban Execution Fix

**Goal:** Server-controlled `HERMES_BOB_TASK_ASSIGNEE` so UI-created tasks spawn with `assignee=default`.

**Status:** Complete — Hermes UI verified on Bob; worker `hermes-assignee` gap is external ops debt

**Artifacts:** `.planning/phases/06F-bob-kanban-execution-fix/`

## Phase 6G: Bob Result Summary Fallback

**Goal:** Show `latest_summary` when kanban `result` is null.

**Status:** Complete — verified on Bob (`t_7b978d4f`)

**Artifacts:** `.planning/phases/06G-bob-result-summary-fallback/`

## Phase 6H: Bob Inbox Summary Enrichment

**Goal:** Richer inbox cards using list enrichment fields.

**Status:** Complete — verified 2026-06-04

**Artifacts:** `.planning/phases/06H-bob-inbox-summary-enrichment/`

## Phase 6I: Bob Inbox UAT Closure

**Goal:** Close 6E human UAT with real Bob Inbox results after 6F–6H.

**Status:** Complete — UAT via SSH tunnel; inbox + detail PASS for `t_7b978d4f`

**Artifacts:** `.planning/phases/06I-bob-inbox-uat-closure/`

## Phase 6J: Bob-First Dashboard Reorder

**Goal:** Prioritize Bob Inbox and task entry above operational status cards.

**Status:** Complete — verified local + Bob deploy

**Artifacts:** `.planning/phases/06J-bob-first-dashboard-reorder/`

## Phase 6K: Long Result Expand UAT

**Goal:** UAT for long-result expand behavior (docs/UAT; harness when no long Bob task).

**Status:** Complete — 2026-06-04

**Artifacts:** `.planning/phases/06K-long-result-expand-uat/`

## Phase 6L: Worker Artifact Visibility

**Goal:** Read-only safe artifact listing in task detail from workspace metadata.

**Status:** Complete — verified on Bob; limited when workspace removed

**Artifacts:** `.planning/phases/06L-worker-artifact-visibility/`

## Phase 6M: Bob Task Queue Hygiene

**Goal:** Read-only assignee labels; `Legacy unassigned` for old ready tasks without assignee.

**Status:** Complete — production-verified on Bob 2026-06-04

**Artifacts:** `.planning/phases/06M-bob-task-queue-hygiene/`

## Phase 6N: Bob UX Milestone Documentation Cleanup

**Goal:** Align planning docs so delmilestone **2.1-bob-ux** (6A–6M) can close.

**Status:** Complete — docs-only 2026-06-04

**Artifacts:** `.planning/phases/06N-bob-ux-milestone-documentation-cleanup/`, `.planning/v2.1-bob-ux-MILESTONE-AUDIT.md`

## Bob Dashboard / Kanban UX (delmilestone 2.1-bob-ux)

**Phases:** 6A–6M (decimal track on top of Phase 5C/5D APIs)

**Status:** **Complete and production-verified** — audit `tech_debt`, no Hermes UI blockers

**Not the same as:** ROADMAP **Phase 6: Operations Enrichment** below (launchctl/Docker read-only cards, OPS-02/03).

**Close with:** `/gsd-complete-milestone 2.1-bob-ux`

## Phase 6: Operations Enrichment

**Goal:** Add richer operational views for launchctl, Docker, and adjacent services where relevant.

**Status:** Not started — next official roadmap phase after closing delmilestone 2.1-bob-ux

**Requirements:** OPS-02, OPS-03

**Note:** Distinct from decimal phases 6A–6M (Bob Dashboard / Kanban UX), which are complete.

**Success criteria:**
1. LaunchAgent detail display uses verified label/plist values.
2. Docker status is added only if Docker becomes relevant to Hermes or adjacent services.
3. Operational cards remain read-only unless a verified write-action phase approves controls.

**Suggested plans:**
- Verify operational sources.
- Add read-only operational status cards.
- Re-run security boundary checks.

## Deferred Phases

These are intentionally outside the first read-only MVP:

- Verified logs viewer after log paths and redaction rules are confirmed.
- Start/stop/restart controls after launchctl commands are verified.
- Audit logging for write actions.
- Rich operational views for Cloudflare Tunnel, launchctl, Docker, and LM Studio.

## Coverage Validation

| Requirement Group | Count | Covered |
|-------------------|-------|---------|
| Project Grounding | 3 | 3 |
| Runtime | 4 | 4 |
| Read-Only API | 4 | 4 |
| Dashboard | 4 | 4 |
| Security | 4 | 4 |

All 19 v1 requirements are mapped to Phase 1 for the first safe read-only MVP.

---
*Roadmap created: 2026-06-03*
