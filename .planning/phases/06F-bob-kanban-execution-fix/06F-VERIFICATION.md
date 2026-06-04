# Phase 6F: Verification

## Local checks

```bash
git status
.venv/bin/python -m pytest -q
grep -R "shell=True" backend/ || true
grep -R "hermes -z" backend/ || true
grep -R "@app.route\\|@.*route" backend/ || true
```

Expected:

- PASS — `.venv/bin/python -m pytest -q`: 69 passed, 1 Starlette/httpx deprecation warning.
- PASS — `grep -R "shell=True" backend/ || true`: no matches.
- PASS — `grep -R "hermes -z" backend/ || true`: no matches.
- PASS — `grep -R "@app.route\\|@.*route" backend/ || true`: no matches.
- PASS — write routes remain covered by tests as existing allowlisted routes only: `POST /api/bob/tasks`, `POST /api/hermes/restart`.
- Bob task create argv includes `--assignee default` only when `HERMES_BOB_TASK_ASSIGNEE=default`.
- Request body cannot control assignee.

## Bob checks

Pending until deploy:

- Bob LaunchAgent/env has `HERMES_BOB_TASK_ASSIGNEE=default`.
- `/api/status` reports `bob_task_assignee=default` and `bob_task_assignee_valid=true`.
- A new task created through existing `POST /api/bob/tasks` has `assignee=default`.
- Dispatcher no longer reports `skipped_unassigned` for the new task.
- If task spawns but ends `blocked/protocol_violation`, keep 6E UAT blocked on Hermes Agent / `kanban-worker` protocol behavior, not Hermes UI task creation.
