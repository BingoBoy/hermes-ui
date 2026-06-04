# Phase 6M: Discussion Log

## 2026-06-04

Bob task history contains old tasks with `assignee=null`, plus newer tasks with `assignee=default` and some blocked worker-environment tasks.

Decision:

- Do not clean up, delete, archive, or mutate tasks in this phase.
- Add read-only clarity in the Bob-oppgaver table:
  - show assignee when present
  - show `Legacy unassigned` for ready tasks without assignee
  - show `Ikke tildelt` for other unassigned statuses
- Keep Inbox behavior unchanged.
