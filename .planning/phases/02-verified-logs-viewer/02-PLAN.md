# Phase 2: Verified Logs Viewer - Plan

**Created:** 2026-06-03
**Status:** Ready for future implementation planning
**Scope:** Log source verification and safe log viewer design only

## Goal

Prepare the future read-only log viewer by verifying Hermes log sources, defining a strict server-side allowlist, and documenting redaction rules. This plan does not implement production log viewer code.

## Atomic Tasks

### Task 1 - Lock Verified Log Sources

**Output:**
- `02-CONTEXT.md`
- `docs/architecture/logging.md`
- updated `.planning/STATE.md`

**Acceptance criteria:**
- LaunchAgent plist path is documented.
- `StandardOutPath` and `StandardErrorPath` are documented as verified.
- Candidate sources are clearly marked as candidate or TBD.
- Excluded sources are documented.

### Task 2 - Define Allowlist and Redaction Contract

**Output:**
- `docs/architecture/logging.md`
- `docs/security/README.md`
- `docs/api/logs.md`

**Acceptance criteria:**
- Future log viewer uses `log_id`, not client-supplied paths.
- Each allowlist entry has `log_id`, display name, absolute path, max lines, redaction flag, and status.
- Redaction rules cover tokens, API keys, Bearer headers, private keys, password fields, Cloudflare credentials, and `.env` lines.
- Failure mode is fail-closed.

### Task 3 - Verify No Runtime Scope Change

**Output:**
- Passing existing tests.
- Security scan confirming no new write actions or log API routes.
- One atomic documentation commit.

**Acceptance criteria:**
- No production log viewer code is added.
- No API route for logs is added.
- No start/stop/restart routes are added.
- No free terminal or shell endpoint is added.
- No secrets are committed.

## Future Implementation Notes

Future implementation should be planned separately and remain read-only:

- Add static log source definitions server-side.
- Add redaction utility with tests.
- Add `GET /api/logs/{log_id}?lines=100`.
- Add dashboard panel only after endpoint tests pass.

---

*Plan created: 2026-06-03*
