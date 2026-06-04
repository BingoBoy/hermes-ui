# Bob Interaction API

How Hermes UI submits a bounded asynchronous task to Bob via Hermes kanban — no browser terminal, chat, or arbitrary CLI.

**Status:** Phase 5C/5D implemented — create and read-only list/show when `ALLOW_BOB_TASKS=true`.

## Goal

Let Truls send a title + body from the Access-protected dashboard. The backend runs a **fixed** `hermes kanban create` argv list. Bob's kanban dispatcher executes the task asynchronously.

## Hermes CLI Path (Bob)

```text
/Users/trulsdahl/.hermes/hermes-agent/venv/bin/hermes
```

At execute time, Hermes UI reads `HERMES_CLI_BIN` (default above). The client never supplies the binary path.

## Kanban CLI Contract

Verified locally on 2026-06-04. **Re-verify on Bob** before deploy (see Preconditions in `.planning/phases/05C-bob-task-entry/05C-PLAN.md`).

### `kanban create`

**Syntax:**

```bash
hermes kanban create <title> [--body BODY] [--idempotency-key KEY] [--json]
```

**Hermes UI fixed argv (allowlisted action `create_kanban_task`):**

```text
hermes kanban create <title> --body <body> --idempotency-key <server-uuid> --json
```

When body is empty after trim, omit `--body` and its value.

| Aspect | Value |
|--------|--------|
| Success exit code | `0` |
| Success stdout | Single JSON object |
| Duplicate key | Same JSON as original task, exit `0` |
| Missing title | Argparse error on stderr, exit `2` |
| Recommended timeout | 30s (`shell=False`) |

**Success JSON (example):**

```json
{
  "id": "t_06aa482f",
  "title": "Hermes UI planning test",
  "body": "Planning verification only",
  "assignee": null,
  "status": "ready",
  "priority": 0,
  "created_at": 1780560167,
  "started_at": null,
  "completed_at": null,
  "result": null
}
```

API maps `id` → `task_id`, `status` → `status`.

### `kanban list` (5D — `GET /api/bob/tasks`)

```bash
hermes kanban list --json
```

| Aspect | Value |
|--------|--------|
| Success exit code | `0` |
| Success stdout | JSON **array** of task objects |
| API query | `limit` default 20, max 50 (server-side slice) |
| API errors | 403 gate off, 502 CLI/parse |

### `kanban show` (5D — `GET /api/bob/tasks/{task_id}`)

```bash
hermes kanban show <task_id> --json
```

| Aspect | Value |
|--------|--------|
| Success exit code | `0` |
| Success stdout | Object with `task`, `comments`, `events`, … |
| Missing task | `no such task: …` with exit **`0`** → API **404** |
| `task_id` | `t_` + alnum/underscore/dash, max 80 chars |
| API errors | 400 invalid id, 404 not found, 403, 502 |

## Rejected Entry Points

| Mechanism | Use in UI? | Reason |
|-----------|------------|--------|
| Gateway HTTP API | No | No UI-facing listen port |
| `hermes send` | No | Outbound notifications only |
| `hermes chat -q -Q` | No (5C) | Agent loop / tools — higher risk |
| `hermes -z` | No | Approval bypass |
| Browser terminal | No | Security policy |
| Client CLI flags | No | Allowlist violation |

## Architecture (5C)

```text
Browser (Cloudflare Access)
  → POST /api/bob/tasks  { title, body }
  → Hermes UI backend (127.0.0.1:8787)
  → subprocess: fixed hermes kanban create argv
  → ~/.hermes kanban.db + gateway dispatcher
```

Read-only status (5D): `GET /api/bob/tasks`, `GET /api/bob/tasks/{task_id}` → `kanban list/show --json`.

## API: POST /api/bob/tasks

**Request:**

```json
{
  "title": "Summarize inbox triage rules",
  "body": "Review current mail triage skill and list gaps."
}
```

**Validation:**

| Field | Max | Rules |
|-------|-----|-------|
| `title` | 200 | Required; no `\n` or `\r`; trimmed |
| `body` | 4000 | Optional; plain text; trimmed |

**Responses:**

| Code | When |
|------|------|
| 202 | Task created (or idempotent hit); body includes `task_id`, `status`, `audit_id` |
| 400 | Validation failed |
| 403 | `ALLOW_BOB_TASKS=false` |
| 429 | Cooldown active (`retry_after` seconds) |
| 502 | CLI failed or stdout not valid JSON |

**Success example (202):**

```json
{
  "success": true,
  "task_id": "t_06aa482f",
  "status": "ready",
  "title": "Summarize inbox triage rules",
  "submitted_at": "2026-06-04T12:00:00+00:00",
  "audit_id": "2026-06-04T12:00:00Z-create_kanban_task-a1b2c3d4"
}
```

**403 example:**

```json
{
  "success": false,
  "detail": "Bob task entry is disabled"
}
```

Idempotency key is **server-generated** (UUID per submit). Not accepted from the client in v1.

## Security Model

| Control | Value |
|---------|--------|
| Feature gate | `ALLOW_BOB_TASKS=false` (default) |
| Allowlisted action | `create_kanban_task` only |
| Subprocess | `shell=False`, fixed argv |
| Cooldown | 60s between successful creates |
| Audit log | `/Users/trulsdahl/.hermes-ui/logs/bob-interactions.log` (JSONL) |
| Audit content | `title_hash`, `body_length` — not full body |
| Output redaction | `backend/redaction.py` on stderr snippets |

Independent of `ALLOW_SERVICE_ACTIONS` (gateway restart).

## Audit Entry (planned)

```json
{
  "timestamp": "2026-06-04T12:00:00+00:00",
  "audit_id": "2026-06-04T12:00:00Z-create_kanban_task-a1b2c3d4",
  "action": "create_kanban_task",
  "task_id": "t_06aa482f",
  "title_hash": "sha256:…",
  "body_length": 42,
  "success": true,
  "exit_code": 0
}
```

## UI (planned)

Section **«Send oppgave til Bob»** on the dashboard:

- Title field, body textarea
- Copy: creates an **async kanban task**, not live chat
- On success: show `task_id` and `audit_id`
- On error: show safe API `detail`
- Form hidden or disabled when `ALLOW_BOB_TASKS=false`

## Bob Verification Checklist (before execute)

```bash
HERMES=/Users/trulsdahl/.hermes/hermes-agent/venv/bin/hermes
KEY="hermes-ui-bob-verify-$(date +%s)"

$HERMES kanban create "Hermes UI Bob verify" --body "Safe test" \
  --idempotency-key "$KEY" --json

$HERMES kanban list --json | head
$HERMES kanban show <id> --json
```

Confirm JSON shape matches this document and dispatcher processes `ready` tasks.

## Sub-Phases

| Phase | Deliverable |
|-------|-------------|
| 5C | POST `/api/bob/tasks` via kanban create |
| 5D | GET task list/detail via kanban list/show | **Implemented** |

## Related Documents

- `docs/api/service-actions.md` — gateway restart (5A)
- `docs/security/README.md` — gates and audit
- `.planning/phases/05C-bob-task-entry/05C-CONTEXT.md` — locked decisions
- `.planning/phases/05-verified-service-actions/05-CONTEXT.md` — parent phase Bob mapping
