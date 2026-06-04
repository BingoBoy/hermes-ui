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

Pending after push: fast-forward pull, `launchctl kickstart -k` for `no.truls.hermes-ui`, curl `/api/operations`.
