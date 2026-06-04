# Phase 6G: Verification

## Local checks

```bash
git status
.venv/bin/python -m pytest -q
grep -R "shell=True" backend/ || true
grep -R "hermes -z" backend/ || true
grep -R "@app.route\\|@.*route" backend/ || true
```

- PASS — `.venv/bin/python -m pytest -q`: 69 passed, 1 Starlette/httpx deprecation warning.
- PASS — `grep -R "shell=True" backend/ || true`: no matches.
- PASS — `grep -R "hermes -z" backend/ || true`: no matches.
- PASS — `grep -R "@app.route\\|@.*route" backend/ || true`: no matches.

## Bob checks

- PASS — local browser smoke on `http://127.0.0.1:8788` loaded dashboard and confirmed Bob Inbox plus `taskResultValue` / `latest_summary` fallback code.
- PASS — deployed commit `f3dfce6` to Bob with fast-forward pull.
- PASS — restarted Hermes UI LaunchAgent with `launchctl kickstart -k gui/$(id -u)/no.truls.hermes-ui`.
- PASS — Bob `/api/status`: `ok`, `bob_task_assignee=default`, `bob_task_assignee_valid=true`.
- PASS — Bob dashboard HTML contains `taskResultValue` and `latest_summary`.
- PASS — `/api/bob/tasks/t_7b978d4f` returns `status=done`, `result=null`, `latest_summary="Morgenbrief for Truls er opprettet."`.
- PASS — Bob repo status clean on `main...origin/main`.

Outcome:

- 6E result action UAT can resume against `t_7b978d4f`: detail/copy rendering now has a summary fallback even when kanban `task.result` is null.
- Full artifact-file display remains out of scope; run metadata file paths are not fetched by the UI in this phase.
