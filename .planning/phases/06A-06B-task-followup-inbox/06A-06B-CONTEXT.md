# Phase 6A–6B: Task Follow-up and Bob Inbox - Context

**Gathered:** 2026-06-04
**Status:** Executed

<domain>

## Phase Boundary

Improve Hermes UI dashboard UX for Bob kanban tasks after 5C/5D — no new write routes, no new backend read routes. Client-side curation uses existing `GET /api/bob/tasks` and `GET /api/bob/tasks/{task_id}`.

</domain>

<decisions>

## Implementation Decisions

- **D-01:** Reuse `ALLOW_BOB_TASKS` gate for inbox and follow-up (no separate read gate).
- **D-02:** Auto-refresh optional checkbox, 12s interval, stops after 3 consecutive API failures.
- **D-03:** Bob Inbox filters client-side: `done`/`completed`/`failed` or non-empty `result`; max 8 items.
- **D-04:** Status normalization: `done` → `completed` badge class for display.
- **D-05:** New task highlighted 8s after POST; detail auto-opens after create.

</decisions>
