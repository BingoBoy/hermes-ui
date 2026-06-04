# Phase 5: Verified Service Actions — Plan

**Created:** 2026-06-04
**Status:** Ready for execute (5A only)
**Scope:** First safe write slice — Hermes Gateway restart with audit and confirmation

## Goal

Deliver restart-only service control for Hermes Gateway (`ai.hermes.gateway`) behind an explicit feature gate, confirmation UX, and append-only audit logging. Start/stop and Bob task entry remain planned for 5B–5D.

## Prerequisites (manual — Truls)

Before `/gsd-execute-phase 5A`:

1. Confirm Bob gateway is healthy after planning verification restart.
2. Set `ALLOW_SERVICE_ACTIONS=true` in local `.env` on Bob when ready to test (keep `false` in repo defaults).
3. Optionally run start/stop verification manually in a maintenance window:

```bash
# On Bob — maintenance window only
launchctl bootout gui/$(id -u) ~/Library/LaunchAgents/ai.hermes.gateway.plist
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/ai.hermes.gateway.plist
launchctl kickstart -k gui/$(id -u)/ai.hermes.gateway
launchctl print gui/$(id -u)/ai.hermes.gateway
```

4. Confirm audit log directory exists: `/Users/trulsdahl/.hermes-ui/logs/`

## Sub-Phases

| ID | Deliverable | Status |
|----|-------------|--------|
| 5A | Restart + audit + confirmation | **Next execute target** |
| 5B | Start/stop actions | Blocked on bootstrap/bootout live verification |
| 5C | Bob task entry via `hermes kanban create` | Blocked on 5A security model + kanban CLI verification |
| 5D | Read-only task/session history | Blocked on 5C |

## Atomic Tasks (5A — max 3)

### Task 1 — Allowlisted Action Runner and Audit Log

**Output:**
- `backend/service_actions.py` — action registry, `_run_allowlisted_action()`, audit writer
- `backend/config.py` — `allow_service_actions`, `hermes_launchd_plist`, `audit_log_path`
- `.env.example` — document new vars
- Unit tests for allowlist rejection, audit append, redaction of stderr

**Acceptance criteria:**
- Only `restart` action exists in registry; `start`/`stop` raise `ActionNotAllowed`.
- Target label hardcoded to `settings.hermes_launchd_label` (`ai.hermes.gateway`).
- Restart argv exactly: `["launchctl", "kickstart", "-k", "gui/{uid}/ai.hermes.gateway"]` with uid from `os.getuid()`.
- No `shell=True`; no client-supplied command strings.
- Audit log writes JSONL with timestamp, action, success, safe detail.
- `ALLOW_SERVICE_ACTIONS=false` (default) prevents execution at module level.

### Task 2 — Restart API Endpoint

**Output:**
- `POST /api/hermes/restart` in `backend/main.py`
- Structured JSON response per `docs/api/service-actions.md`
- Integration tests with mocked subprocess
- Update `tests/test_api.py` — write route allowed only when explicitly testing; default test suite verifies gate behavior

**Acceptance criteria:**
- Returns `403` when `ALLOW_SERVICE_ACTIONS=false`.
- Returns structured success/failure JSON; no tracebacks in response body.
- Post-action includes refreshed `hermes_status` block from existing read-only provider.
- 30s cooldown prevents rapid repeat restarts (return `429` with safe message).
- Existing read-only routes unchanged.

### Task 3 — Dashboard Confirmation and Docs

**Output:**
- Restart button on Hermes Gateway card with confirmation modal
- `docs/api/service-actions.md`, `docs/security/README.md`, `docs/architecture/deployment.md` updated
- `.planning/STATE.md` updated after verification

**Acceptance criteria:**
- Button disabled/hidden when `read_only: true` in status payload (or separate capability flag from API).
- User must confirm in modal before POST fires.
- Dashboard shows action result (success/error) without raw stderr.
- Manual verification on Bob: restart via UI, audit log entry present, gateway returns to running.
- `pytest` passes; secret scan clean.

## Verification Checklist

- [ ] `git status` — no accidental `.env` or secrets
- [ ] `.venv/bin/python -m pytest` — all tests pass
- [ ] Secret scan — no tokens committed
- [ ] Unauthenticated external curl still returns HTTP 302 (Cloudflare Access)
- [ ] `ALLOW_SERVICE_ACTIONS=false` → POST returns 403
- [ ] Audit log entry created on successful restart

## Out of Scope for 5A Execute

- Start/stop endpoints
- Bob kanban task submission
- Chat UI
- Cloudflare or LaunchAgent plist changes
- `hermes gateway` CLI delegation

---

*Plan created: 2026-06-04*
