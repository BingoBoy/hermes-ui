# Phase 6F: Discussion Log

## 2026-06-04

- `POST /api/bob/tasks` accepts `title` and `body` only.
- `backend/bob_tasks.py` builds fixed argv for `hermes kanban create`; no `shell=True`, no `hermes -z`, no client CLI flags.
- Current create argv omits `--assignee`, so Bob tasks are created with `assignee=null`.
- Bob dispatcher skips UI-created tasks as `skipped_unassigned`.
- Manual `--assignee bob` produced `skipped_nonspawnable`.
- Manual `--assignee default` spawned; `hermes profile list` shows `default` as the only profile.
- A spawned default task later ended `blocked/protocol_violation` because the worker exited without `kanban_complete` or `kanban_block`.

Decision:

- Add optional server-controlled `HERMES_BOB_TASK_ASSIGNEE`, recommended Bob production value `default`.
- Validate assignee with a strict simple profile pattern: letters, digits, `_`, `-`, `.`.
- Never accept assignee from request body.
- Treat remaining `blocked/protocol_violation` as a Hermes Agent / `kanban-worker` protocol problem unless it can be fixed safely without editing Hermes Agent source.
