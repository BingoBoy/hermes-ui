# Phase 6H: Verification

## Local checks

```bash
git status
.venv/bin/python -m pytest -q
grep -R "shell=True" backend/ || true
grep -R "hermes -z" backend/ || true
grep -R "@app.route\\|@.*route" backend/ || true
```

- PASS — `.venv/bin/python -m pytest -q`: 71 passed, 1 Starlette/httpx deprecation warning.
- PASS — `grep -R "shell=True" backend/ || true`: no matches.
- PASS — `grep -R "hermes -z" backend/ || true`: no matches.
- PASS — `grep -R "@app.route\\|@.*route" backend/ || true`: no matches.

## Bob checks

- PASS — deployed commit `98bad83` to Bob with fast-forward pull.
- PASS — restarted Hermes UI LaunchAgent with `launchctl kickstart -k gui/$(id -u)/no.truls.hermes-ui`.
- PASS — `/api/status`: `ok`, `allow_bob_tasks=True`, `bob_task_assignee=default`, `bob_task_assignee_valid=True`.
- PASS — `/api/bob/tasks?limit=50` now includes `latest_summary="Morgenbrief for Truls er opprettet."` for `t_7b978d4f`.
- PASS — Bob repo status clean on `main...origin/main`.

Outcome:

- Bob Inbox can now receive summary text directly from the existing list API for completed tasks whose kanban `result` is null.
- 6E copy/expand UAT can proceed from the Inbox card as well as the task detail panel.
