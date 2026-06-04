# Phase 5C Plan: Bob Task Entry via Hermes Kanban

**Goal:** Implement safe Bob task creation from Hermes UI using fixed `hermes kanban create` argv only.

**Depends on:** 5A security patterns (audit, gates, subprocess); Bob live kanban verify (gate below)

**Status:** Executed locally 2026-06-04 — Bob deploy verification pending

## Preconditions (Truls on Bob before Task 1 merge)

```bash
HERMES=/Users/trulsdahl/.hermes/hermes-agent/venv/bin/hermes
KEY="hermes-ui-bob-verify-$(date +%s)"

$HERMES kanban create "Hermes UI Bob verify" --body "Safe test — archive later" \
  --idempotency-key "$KEY" --json

$HERMES kanban list --json | head
$HERMES kanban show <id-from-create> --json

# Confirm dispatcher picks up ready tasks (gateway running)
launchctl print gui/$(id -u)/ai.hermes.gateway | head -5
```

Record: exit codes, JSON fields, whether task moves from `ready` → `running` without manual `kanban dispatch`.

## Atomic Tasks (max 3)

### Task 1 — `backend/bob_tasks.py` + tests

- Add `create_kanban_task(settings, title, body)` with fixed argv builder
- Validation: title/body limits, newline rejection, trim
- `ALLOW_BOB_TASKS` check → `BobTasksDisabled`
- Cooldown 60s, audit JSONL to `bob-interactions.log`
- Parse create JSON stdout → `task_id`, `status`
- Tests: argv shape, gate off, cooldown, validation, audit append, no `shell=True` in source, mock runner success/failure
- **Commit:** `feat(5C): add allowlisted bob kanban task runner`

### Task 2 — API route + config

- `config.py`: `allow_bob_tasks`, `hermes_cli_bin` (default Bob path), audit path env
- `POST /api/bob/tasks` in `main.py` → 202/400/403/429/502
- `.env.example`: document `ALLOW_BOB_TASKS=false`, `HERMES_CLI_BIN=`
- **Commit:** `feat(5C): add POST /api/bob/tasks with feature gate`

### Task 3 — Dashboard + docs

- Dashboard section «Send oppgave til Bob» (title, body, submit, success/error, task_id + audit_id)
- Update `docs/api/bob-interaction.md`, `docs/security/README.md`, `docs/architecture/deployment.md`
- **Commit:** `feat(5C): add Bob task form and document kanban contract`

## Verification (execute)

```bash
pytest
rg 'shell=True' backend/
rg 'hermes -z|chat -q' backend/   # expect no matches
# secret scan per project habit
curl -s -X POST http://127.0.0.1:8787/api/bob/tasks -H 'Content-Type: application/json' \
  -d '{"title":"test","body":"x"}'   # 403 when gate off
```

## Out of Scope (5C)

- `GET /api/bob/tasks` (5D)
- Chat, terminal, `hermes -z`
- LaunchAgent / Cloudflare changes
- Start/stop gateway

## Success Criteria

1. With `ALLOW_BOB_TASKS=true`, POST creates kanban task and returns `task_id` + `audit_id`.
2. With gate false, POST returns 403.
3. No `shell=True`; no client-controlled CLI flags.
4. Audit log contains no full body text.
