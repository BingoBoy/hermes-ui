# Bob Interaction API

How Hermes UI submits a bounded asynchronous task to Bob via Hermes kanban — no browser terminal, chat, or arbitrary CLI.

**Status:** Phase 5C/5D implemented; Phase 6F adds optional server-controlled assignee — create and read-only list/show when `ALLOW_BOB_TASKS=true`.

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
hermes kanban create <title> [--body BODY] [--assignee PROFILE] [--idempotency-key KEY] [--json]
```

**Hermes UI fixed argv (allowlisted action `create_kanban_task`):**

```text
hermes kanban create <title> --body <body> [--assignee <server-profile>] --idempotency-key <server-uuid> --json
```

When body is empty after trim, omit `--body` and its value. When `HERMES_BOB_TASK_ASSIGNEE` is unset, omit `--assignee` and its value. The client never supplies assignee.

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
  "assignee": "default",
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
  → subprocess: fixed hermes kanban create argv + optional server assignee
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
  "assignee": "default",
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

Assignee is **server-controlled** via `HERMES_BOB_TASK_ASSIGNEE`. The value is optional, strictly validated as a simple profile string (`A-Z`, `a-z`, `0-9`, `_`, `-`, `.`), and never accepted from the request body.

## Security Model

| Control | Value |
|---------|--------|
| Feature gate | `ALLOW_BOB_TASKS=false` (default) |
| Allowlisted action | `create_kanban_task` only |
| Subprocess | `shell=False`, fixed argv |
| Assignee | Optional server env `HERMES_BOB_TASK_ASSIGNEE`; recommended Bob production value: `default` |
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

## UI

Sections on the dashboard (when `ALLOW_BOB_TASKS=true`):

### Send oppgave til Bob (5C)

- Title field, body textarea
- Copy: creates an **async kanban task**, not live chat
- On success: show `task_id` and `audit_id`

### Bob task-maler (6C + 6D)

- Compact template rows above the manual form (frontend-only, hardcoded prompts)
- Optional text fields per template (6D) — values are merged into the task `body` in the browser only
- «Send mal til Bob» calls the same `POST /api/bob/tasks` with composed `title` + `body` — no extra API fields or CLI flags
- Templates: Morgenbrief, Ukesrapport, Konkurrentanalyse, Nettsideanalyse, Markedsføringsstatus
- Hidden when `ALLOW_BOB_TASKS=false`
- No terminal, chat, shell, or user-defined templates

**Template inputs (6D):**

| Mal | Felt | Effekt på `body` |
|-----|------|------------------|
| Morgenbrief | Fokus for dagen (valgfritt) | Appends `Dagens fokus: …` when set |
| Ukesrapport | Periode (valgfritt) | Defaults to «denne uken» in prompt when empty |
| Konkurrentanalyse | Konkurrent eller tema (valgfritt) | Appends focus line when set |
| Nettsideanalyse | URL (valgfritt) | Appends URL line when set; empty keeps ask-for-URL instruction |
| Markedsføringsstatus | Fokusområde (valgfritt) | Appends focus area when set |

### Bob-oppgaver (5D + 6A)

- Task table with status badges (ready, running, completed, failed, unknown)
- Timestamps: created, started, completed
- Optional auto-refresh every 12 seconds (toggle)
- Detail panel with result text/JSON and technical JSON in `<details>`

### Bob Inbox (6B + 6E)

- Read-only inbox of up to 8 newest completed/failed/result tasks
- Result excerpt with **Vis mer** / **Vis mindre** for long text (6E)
- **Kopier resultat**, **Kopier ID**, **Kopier tittel** — browser clipboard only (6E)
- Task meta line (ID + timestamps) on each card (6E)
- **Vis detaljer** opens the task detail panel below Bob-oppgaver
- Empty state: «Ingen ferdige Bob-resultater ennå.»

### Bob result actions (6E)

- Frontend-only — no new API routes or Bob/Hermes state changes
- Copy uses `navigator.clipboard.writeText` with a safe `execCommand` fallback
- Same actions on the **Oppgavedetaljer** result panel when a result exists
- Feedback: «Kopiert» / «Kunne ikke kopiere»
- No delete, archive, or mark-read in this phase

## Bob Verification Checklist (before execute)

```bash
HERMES=/Users/trulsdahl/.hermes/hermes-agent/venv/bin/hermes
KEY="hermes-ui-bob-verify-$(date +%s)"

$HERMES kanban create "Hermes UI Bob verify" --body "Safe test" \
  --assignee default --idempotency-key "$KEY" --json

$HERMES kanban list --json | head
$HERMES kanban show <id> --json
```

Confirm JSON shape matches this document and dispatcher does not report `skipped_unassigned` for the new task. If the task spawns but later ends `blocked/protocol_violation`, treat that as a separate Hermes Agent / `kanban-worker` protocol issue.

## Sub-Phases

| Phase | Deliverable |
|-------|-------------|
| 5C | POST `/api/bob/tasks` via kanban create |
| 5D | GET task list/detail via kanban list/show | **Implemented** |
| 6A–6B | Dashboard follow-up + Bob Inbox | **Implemented** (UI only) |
| 6C | Bob task-maler (templates) | **Implemented** (UI only) |
| 6D | Template inputs (optional fields → task text) | **Implemented** (UI only) |
| 6E | Bob result actions (copy + expand) | **Implemented** (UI only) |

## Related Documents

- `docs/api/service-actions.md` — gateway restart (5A)
- `docs/security/README.md` — gates and audit
- `.planning/phases/05C-bob-task-entry/05C-CONTEXT.md` — locked decisions
- `.planning/phases/05-verified-service-actions/05-CONTEXT.md` — parent phase Bob mapping
