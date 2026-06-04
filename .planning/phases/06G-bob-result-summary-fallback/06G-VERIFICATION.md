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

Pending:

- Deploy commit to Bob.
- Confirm `/api/bob/tasks/t_7b978d4f` still exposes `latest_summary`.
- Confirm dashboard detail/result helpers can use `latest_summary` when `task.result` is null.
- Confirm no new write routes or client-controlled CLI flags were introduced.
