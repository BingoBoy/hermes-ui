# Project Milestones: Hermes UI for Bob

## ROADMAP Phase 6: Operations Enrichment (Shipped: 2026-06-04)

**Delivered:** Read-only operational views — `GET /api/operations`, dashboard «Drift og tjenester», LaunchAgent metadata for Hermes UI and gateway.

**Requirements:** OPS-02, OPS-03

**Production:** Bob `@8632f49` (feat); `/api/operations` verified; Docker off on Bob.

**Git range:** `01d04f8` → `8632f49`

---

## v2.1-bob-ux: Bob Dashboard / Kanban UX (Shipped: 2026-06-04)

**Status:** Completed and archived.

**Delivered:** Safe Bob task communication in the Hermes UI dashboard — inbox, templates, results, assignee, artifacts, and queue labels on top of Phase 5C/5D APIs.

**Phases completed:** 6A–6N (14 phase entries; 6N docs-only closure)

**Key accomplishments:**

- Bob Inbox and Bob-oppgaver follow-up with auto-refresh
- Five one-click task templates with optional per-template inputs
- Copy/expand result actions (UAT closed via 6I on `t_7b978d4f`)
- Server-side `HERMES_BOB_TASK_ASSIGNEE=default` for task spawn
- `latest_summary` fallback when kanban `result` is null
- Bob-first dashboard section order
- Read-only safe worker artifacts in task detail
- Assignee column with `Legacy unassigned` for old ready tasks

**Archives:**

- Roadmap: `.planning/milestones/v2.1-bob-ux-ROADMAP.md`
- Requirements: `.planning/milestones/v2.1-bob-ux-REQUIREMENTS.md`
- Audit: `.planning/milestones/v2.1-bob-ux-MILESTONE-AUDIT.md`

---

## What's next

Phases **v2.1-bob-ux** and **ROADMAP Phase 6** are shipped. No active roadmap phase selected.

**Recommended:**

1. `/gsd-audit-uat` or `/gsd-audit-milestone` — reconcile planning vs production
2. Choose next work from `.planning/ROADMAP.md` **Backlog** (e.g. 5B, OPS-01, UI logs) via `/gsd-discuss-phase` or `/gsd-add-phase`

**Not automatic:** `/gsd-complete-milestone` for whole project until audit clarifies scope.
