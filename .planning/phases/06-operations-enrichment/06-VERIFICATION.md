# Phase 6: Verification

## Bob preflight (6.1)

- PASS — `launchctl print gui/501/no.truls.hermes-ui` — state `running`, path matches plist.
- PASS — `launchctl print gui/501/ai.hermes.gateway` — state `running`.
- PASS — Both plists readable; labels match `deployment.md`.
- PASS — Docker: `which docker` not found on Bob → `HERMES_OPS_INCLUDE_DOCKER=false` (OPS-03 assessed, not applicable).

## Local checks

```bash
.venv/bin/python -m pytest -q
grep -R "shell=True" backend/ || true
grep -R "hermes -z" backend/ || true
```

- PASS — pytest: 77 passed.
- PASS — `shell=True`: no matches.
- PASS — `hermes -z`: no matches.
- PASS — `GET /api/operations` returns two launch agents + docker `included: false`.
- PASS — Dashboard includes `operations-section` between Bob history and status cards.

## Bob deploy (6.6)

- PASS — Bob pulled `8632f49`, restarted `no.truls.hermes-ui`.
- PASS — `/api/operations`: `read_only=true`, agents `no.truls.hermes-ui` + `ai.hermes.gateway`, `docker.included=false`.
- PASS — Assignee/status unchanged: `/api/status` ok, `bob_task_assignee=default`.

Outcome: Phase 6 Operations Enrichment production-verified on Bob loopback.
