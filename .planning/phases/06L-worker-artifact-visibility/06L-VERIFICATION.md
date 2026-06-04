# Phase 6L: Verification

## Local checks

```bash
.venv/bin/python -m pytest -q
grep -R "shell=True" backend/ || true
grep -R "hermes -z" backend/ || true
grep -R "@app.route\\|@.*route" backend/ || true
```

- PASS — `.venv/bin/python -m pytest -q`: 74 passed, 1 Starlette/httpx deprecation warning.
- PASS — `grep -R "shell=True" backend/ || true`: no matches.
- PASS — `grep -R "hermes -z" backend/ || true`: no matches.
- PASS — `grep -R "@app.route\\|@.*route" backend/ || true`: no matches.

## Bob checks

- PASS — deployed commit `2cb394a` to Bob with fast-forward pull.
- PASS — restarted Hermes UI LaunchAgent with `launchctl kickstart -k gui/$(id -u)/no.truls.hermes-ui`.
- PASS — `/api/status`: `ok`, `allow_bob_tasks=True`, `bob_task_assignee=default`.
- PASS — Bob repo status clean on `main...origin/main`.
- LIMITED — `/api/bob/tasks/t_7b978d4f` returned no `artifacts` because `/Users/trulsdahl/.hermes/kanban/workspaces/t_7b978d4f` no longer exists on Bob.

Outcome:

- Safe artifact visibility is implemented and covered locally, including path escape rejection.
- Historical artifact UAT against `t_7b978d4f` could not render because the worker workspace has been removed.
- Next real Bob task that keeps a metadata `file_path` under its workspace and within size/suffix limits should show `Artifakter` and `Kopier artifakt` in task detail.
