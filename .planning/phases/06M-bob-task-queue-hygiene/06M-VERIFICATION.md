# Phase 6M: Verification

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

- PASS — deployed commit `1cd4e06` to Bob with fast-forward pull.
- PASS — restarted Hermes UI LaunchAgent with `launchctl kickstart -k gui/$(id -u)/no.truls.hermes-ui`.
- PASS — Bob dashboard HTML includes `Assignee`, `Legacy unassigned`, and `assigneeDisplayLabel`.
- PASS — Bob repo status clean on `main...origin/main`.

Outcome:

- Bob-oppgaver now labels unassigned ready tasks as `Legacy unassigned`.
- No queue mutation was performed.
