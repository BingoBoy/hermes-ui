# Phase 6J: Verification

## Local checks

```bash
.venv/bin/python -m pytest -q
grep -R "shell=True" backend/ || true
grep -R "hermes -z" backend/ || true
grep -R "@app.route\\|@.*route" backend/ || true
```

- PASS — `.venv/bin/python -m pytest -q`: 72 passed, 1 Starlette/httpx deprecation warning.
- PASS — `grep -R "shell=True" backend/ || true`: no matches.
- PASS — `grep -R "hermes -z" backend/ || true`: no matches.
- PASS — `grep -R "@app.route\\|@.*route" backend/ || true`: no matches.

## Browser smoke

- PASS — local dashboard loaded on `http://127.0.0.1:8788`.
- PASS — first main sections were:
  1. `bob-inbox-section`
  2. `bob-task-section`
  3. `bob-history-section`
  4. `Statuskort`
  5. `Gateway-logger`
- PASS — first viewport shows Bob Inbox and Send oppgave til Bob before operational status.

## Bob deploy

- PASS — deployed commit `c8bf243` to Bob with fast-forward pull.
- PASS — restarted Hermes UI LaunchAgent with `launchctl kickstart -k gui/$(id -u)/no.truls.hermes-ui`.
- PASS — Bob dashboard HTML order:
  1. `bob-inbox-section`
  2. `bob-task-section`
  3. `bob-history-section`
  4. `Statuskort`
  5. `Gateway-logger`
- PASS — Bob repo status clean on `main...origin/main`.
