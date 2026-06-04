# Phase 5C Discussion Log

**Date:** 2026-06-04
**Mode:** Auto (user supplied full scope and constraints)
**Phase:** 5C — Bob Task Entry via Hermes Kanban

## Scope Confirmed

- Discuss/plan only — no runtime write routes in this session
- Entry: `hermes kanban create --json` only
- Excluded: chat, terminal, `hermes -z`, shell, client CLI flags, Cloudflare/LaunchAgent changes, start/stop

## Areas Covered (auto-selected)

### 1. Kanban CLI contract

**Decision:** Fixed argv create with server-generated `--idempotency-key`; map CLI `id` to API `task_id`.

**Evidence (local verification):**

```bash
hermes kanban create "title" --body "body" --idempotency-key <uuid> --json  # exit 0, JSON object
hermes kanban list --json   # exit 0, JSON array
hermes kanban show <id> --json  # exit 0, { task, events, ... }
hermes kanban show t_bad --json  # "no such task" but exit 0 — document parser quirk
```

Bob binary path: `/Users/trulsdahl/.hermes/hermes-agent/venv/bin/hermes`

### 2. Security model

**Decision:** `ALLOW_BOB_TASKS=false` default; action `create_kanban_task` only; title/body limits; audit JSONL without full body; 60s cooldown; `shell=False`.

**Aligned with:** `backend/service_actions.py` patterns from 5A.

### 3. API and UI

**Decision:** `POST /api/bob/tasks` with `{title, body}`; 403/400/429/202; dashboard section «Send oppgave til Bob» with async-task explanation.

### 4. Deferred

- 5D read-only list/show
- chat -q sync path
- chat UI

## Claude's Discretion

- Cooldown 60s (vs restart 30s)
- Hide vs disable task form when gate off (implementer choice)

## Preflight (2026-06-04)

**Testmiljø:** `ModuleNotFoundError: backend` skyldtes at `pytest`-skriptet ikke la prosjektroten på `sys.path` (i motsetning til `python -m pytest`). Løst med `pytest.ini` → `pythonpath = .`.

**Verifisert lokalt:**

- `0a26a1e` på `main`
- `.venv/bin/pytest` og `.venv/bin/python -m pytest` → 25 passed
- Ingen `backend/bob_tasks.py`; ingen `POST /api/bob/tasks` i `backend/`
- `test_only_allowlisted_write_route_exists` → kun `POST /api/hermes/restart`
- Ingen `shell=True` i `backend/` (kun negativ assert i tester)

**Gjenstår før 5C execute på Bob:** kanban create/list/show med Bob-binær (se `05C-PLAN.md` Preconditions).

## Execute (2026-06-04)

- Backend, API, dashboard, and docs implemented
- 46 pytest passed locally
- Bob deploy: enable `ALLOW_BOB_TASKS=true` after on-host kanban verify
