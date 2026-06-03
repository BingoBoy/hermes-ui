# Phase 2: Verified Logs Viewer - Plan

**Created:** 2026-06-03
**Status:** Complete
**Scope:** Bounded read-only log viewer implementation

## Goal

Implement a bounded read-only log viewer using verified Hermes log paths and a strict server-side allowlist. No write actions, no client-supplied paths, and mandatory redaction before response.

## Atomic Tasks

### Task 1 - Allowlist and Redaction

**Output:**
- `backend/log_sources.py`
- `backend/redaction.py`
- `backend/logs.py`
- unit tests for redaction and allowlist behavior

**Acceptance criteria:**
- Only `gateway_stdout` and `gateway_stderr` are enabled.
- Candidate sources remain disabled.
- Redaction masks tokens, API keys, Bearer headers, private keys, password fields, Cloudflare credentials, and `.env`-style lines.

### Task 2 - Logs API

**Output:**
- `GET /api/logs/sources`
- `GET /api/logs/{source_id}?lines=100`

**Acceptance criteria:**
- Unknown `source_id` returns safe `404`.
- Missing log file returns structured safe error without traceback.
- `lines` defaults to 100 and is capped at 500.
- Responses never include raw secrets.

### Task 3 - Dashboard, Tests, and Docs

**Output:**
- Updated dashboard log panels
- Extended tests and documentation

**Acceptance criteria:**
- Dashboard shows allowlisted log sources and bounded previews.
- All tests pass.
- No new write-action routes are introduced.

---

*Plan created: 2026-06-03*
## Completion

Phase 2 completed on 2026-06-03:

- Allowlist and redaction modules implemented.
- Logs API endpoints implemented.
- Dashboard, tests, and documentation updated.
- All tests passed.

*Plan updated: 2026-06-03 for implementation*
*Plan completed: 2026-06-03*
