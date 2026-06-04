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

Pending:

- Deploy to Bob.
- Confirm `/api/bob/tasks?limit=50` now includes `latest_summary` for `t_7b978d4f`.
- Confirm Bob dashboard still serves 6G fallback code.
- Confirm no new routes/write actions.
