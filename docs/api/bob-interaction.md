# Bob Interaction API (Planned)

How Hermes UI can safely submit a bounded task to Bob/Hermes without a browser terminal or arbitrary command runner.

**Status:** Planning only — not implemented until Phase 5C execute.

## Goal

Let Truls send a simple text task from Hermes UI and later see status or outcome, while keeping:

- No free shell in the browser
- No client-defined commands
- No secrets in requests or responses
- Cloudflare Access as outer auth layer

## What Was Mapped on Bob (2026-06-04)

| Mechanism | Safe for UI? | Notes |
|-----------|--------------|-------|
| Hermes Gateway HTTP API | No | Gateway runs as launchd process; no dedicated listen port found for UI ingress |
| Telegram / messaging gateway | Indirect | Inbound via configured channels; not a UI-native API |
| `hermes send` | No (wrong direction) | Outbound notifications to Telegram/Discord/Slack — scripts/CI use case |
| `hermes chat -q "..." -Q` | Caution | Single programmatic query; agent loop with tools — needs strict caps |
| `hermes -z "..."` | No | Oneshot with approval bypass — too permissive for web UI |
| `hermes kanban create` | **Yes (preferred)** | Durable task queue, bounded title/body, idempotency key, async dispatch |
| `hermes webhook subscribe` | Later | Event-driven; requires Hermes webhook HTTP surface setup |
| `hermes sessions list` | Read-only (5D) | History inspection for completed work |

Hermes CLI path on Bob:

```text
/Users/trulsdahl/.hermes/hermes-agent/venv/bin/hermes
```

## Recommended Architecture (5C)

```text
Browser (Cloudflare Access)
    → POST /api/bob/tasks  (Hermes UI backend)
    → fixed argv: hermes kanban create "<title>" --body "<body>" --idempotency-key <uuid> --json
    → kanban.db / dispatcher on Bob
    → read-only poll: GET /api/bob/tasks/{id}  (5D)
    → fixed argv: hermes kanban show <id> --json
```

### Why kanban first

- **Async by design** — UI submits task, polls status; no long HTTP hold open.
- **Idempotency** — `--idempotency-key` prevents duplicate submits on refresh/retry.
- **Bounded input** — title + body only; no arbitrary CLI flags from client.
- **Existing infrastructure** — `kanban.db` already present under `~/.hermes/`.
- **Audit-friendly** — kanban maintains task events and comments.

### Alternative: synchronous chat query (5C-b, optional)

```text
POST /api/bob/query
→ hermes chat -q "<prompt>" -Q --max-turns 1
```

Constraints if used:

- Max prompt length 2000 chars
- No `--yolo`, no `--accept-hooks`, no model/provider from client
- Timeout 120s with safe partial response handling
- Higher risk than kanban — defer unless kanban latency is unacceptable

## Planned Endpoints

### POST /api/bob/tasks (5C)

Submit a bounded task to Bob.

**Request body (planned):**

```json
{
  "title": "Summarize inbox triage rules",
  "body": "Review current mail triage skill and list gaps.",
  "idempotency_key": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Validation:**

| Field | Max length | Rules |
|-------|------------|-------|
| `title` | 200 | Required, no newlines |
| `body` | 4000 | Optional, plain text |
| `idempotency_key` | 64 | UUID format, server-generated if omitted |

**Success response (202):**

```json
{
  "success": true,
  "task_id": "t42",
  "status": "todo",
  "title": "Summarize inbox triage rules",
  "submitted_at": "2026-06-04T11:00:00+00:00",
  "audit_id": "2026-06-04T11:00:00Z-task-xyz"
}
```

### GET /api/bob/tasks (5D)

List recent tasks (read-only, bounded).

**Query:** `limit=20` (max 50)

Backend runs fixed `hermes kanban list --json`, parses and redacts output.

### GET /api/bob/tasks/{task_id} (5D)

Task detail with comments/events.

Backend runs fixed `hermes kanban show {task_id} --json`.

## Audit Logging (Bob Interactions)

Separate log or shared audit file:

```text
/Users/trulsdahl/.hermes-ui/logs/bob-interactions.log
```

Each entry:

```json
{
  "timestamp": "2026-06-04T11:00:00+00:00",
  "audit_id": "2026-06-04T11:00:00Z-task-xyz",
  "action": "kanban_create",
  "task_id": "t42",
  "title_hash": "sha256:...",
  "success": true
}
```

Do not log full body if it may contain sensitive content — store hash + length only, or redact PII per `backend/redaction.py`.

## Input and Output Safety

- All Hermes CLI output passes through `redaction.py` before JSON response.
- No raw `~/.hermes/.env`, `config.yaml`, or session DB paths exposed.
- Fail closed on CLI errors — structured safe `detail`, no tracebacks.
- Feature gate: `ALLOW_BOB_TASKS=false` (default) — parallel to `ALLOW_SERVICE_ACTIONS`.

## Explicitly Out of Scope

- Chat UI / streaming tokens
- Browser terminal
- Client-specified Hermes flags (`--yolo`, `--skills`, model overrides)
- Direct Telegram send from UI
- Exposing Hermes internal config or credentials

## Verification Required Before 5C Execute

On Bob, in a safe test window:

```bash
HERMES=/Users/trulsdahl/.hermes/hermes-agent/venv/bin/hermes

# Create dry-run task
$HERMES kanban create "Hermes UI test task" --body "Planning verification only" --json

# List and show
$HERMES kanban list --json | head
$HERMES kanban show <id> --json

# Confirm dispatcher behavior (optional)
$HERMES kanban dispatch --help
```

Document exit codes, JSON schema, and whether kanban dispatcher auto-runs or needs manual `kanban dispatch`.

## Sub-Phase Mapping

| Phase | Deliverable |
|-------|-------------|
| 5C | POST `/api/bob/tasks` via kanban create |
| 5D | GET task list/detail + optional sessions summary |

## Related Documents

- `docs/api/service-actions.md` — gateway restart (Track A)
- `docs/security/README.md` — write-action gates
- `.planning/phases/05-verified-service-actions/05-CONTEXT.md` — locked decisions
