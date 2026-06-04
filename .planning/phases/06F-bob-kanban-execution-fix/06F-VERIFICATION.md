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

Deployed on Bob on 2026-06-04:

- PASS — Bob pulled `main` to commit `317f6ff`.
- PASS — Bob LaunchAgent plist now has `HERMES_BOB_TASK_ASSIGNEE=default`.
- NOTE — `launchctl kickstart -k gui/$(id -u)/no.truls.hermes-ui` did not reload the updated EnvironmentVariables. A `bootout` + `bootstrap` was required.
- PASS — `/api/status` reports `bob_task_assignee=default`, `bob_task_assignee_configured=true`, and `bob_task_assignee_valid=true`.
- PASS — Existing `POST /api/bob/tasks` created `t_be47ac55` with `assignee=default`.
- PASS — `hermes kanban dispatch --json` spawned `t_be47ac55` with `assignee=default`; it was not in `skipped_unassigned`.

Worker result:

- BLOCKED — `t_be47ac55` later ended `blocked`.
- Reason: `Missing command: hermes-assignee not found in the environment.`
- Task log: `/Users/trulsdahl/.hermes/kanban/logs/t_be47ac55.log`.
- Log evidence: worker ran `hermes-assignee verify`, exit `127`; `which hermes-assignee`, exit `1`; then called `kanban_block`.
- This is a separate Hermes Agent / `kanban-worker` environment issue. Hermes UI task creation is no longer blocked by unassigned tasks, but 6E UAT still cannot resume to completed-result validation until the worker environment has the expected `hermes-assignee` command or the worker task prompt/skill behavior is corrected.
