# Phase 6G: Discussion Log

## 2026-06-04

- After 6F, Bob task assignment works: new UI tasks use `assignee=default` and dispatch spawns them.
- One verification task (`t_be47ac55`) blocked because the worker attempted `hermes-assignee verify`; Bob's worker environment did not have `hermes-assignee`.
- A normal template task (`t_7b978d4f`, `Lag morgenbrief`) completed successfully with `status=done`.
- The completed task shape is important:
  - `task.result` is `null`.
  - `latest_summary` is `"Morgenbrief for Truls er opprettet."`.
  - run metadata points to `/Users/trulsdahl/.hermes/kanban/workspaces/t_7b978d4f/morgenbrief.md`.
- Current dashboard result helpers only use `task.result`, so copy/expand/detail result actions can miss a valid completed summary.

Decision:

- Treat `latest_summary` as a safe read-only display/copy fallback.
- Do not fetch metadata files or workspace paths in this phase.
- Keep Inbox/detail behavior browser-only; no new API routes or mutations.
