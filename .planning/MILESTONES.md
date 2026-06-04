# Project Milestones: Hermes UI for Bob

## v2.1-bob-ux Bob Dashboard / Kanban UX (Shipped: 2026-06-04)

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

**Stats:**

- Git range: `9fff380` → `bbfdce7`
- ~7 code files touched in milestone range (`dashboard.py`, `bob_tasks.py`, tests)
- Audit verdict: `tech_debt` (worker `hermes-assignee` external; no UI blockers)
- Known deferred at close: see `.planning/milestones/v2.1-bob-ux-MILESTONE-AUDIT.md`

**Archives:**

- Roadmap: `.planning/milestones/v2.1-bob-ux-ROADMAP.md`
- Requirements: `.planning/milestones/v2.1-bob-ux-REQUIREMENTS.md`
- Audit: `.planning/milestones/v2.1-bob-ux-MILESTONE-AUDIT.md`

**What's next:** ROADMAP **Phase 6: Operations Enrichment** (`/gsd-plan-phase 6`) — distinct from this decimal track.

---
