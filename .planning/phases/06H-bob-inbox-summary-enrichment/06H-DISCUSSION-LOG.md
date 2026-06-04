# Phase 6H: Discussion Log

## 2026-06-04

- `hermes kanban list --json` for completed task `t_7b978d4f` returns `result=null` and no `latest_summary`.
- `GET /api/bob/tasks?limit=50` returns the same shape because it wraps list output.
- `GET /api/bob/tasks/t_7b978d4f` returns `latest_summary="Morgenbrief for Truls er opprettet."`.
- Bob Inbox is rendered from list data, so 6G detail fallback alone does not give Inbox cards direct summary/copy text.

Decision:

- Keep the existing read-only list route.
- Enrich at most 8 completed/failed/blocked list tasks per request with `latest_summary` from fixed `kanban show`.
- Skip enrichment silently for individual show failures so list remains robust.
- Do not read worker metadata files in this phase.
