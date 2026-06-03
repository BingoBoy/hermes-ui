# Roadmap: Hermes UI for Bob

**Created:** 2026-06-03
**Granularity:** Standard
**Flow:** discuss -> plan -> execute -> verify

## Overview

| Phase | Name | Goal | Requirements | UI hint |
|-------|------|------|--------------|---------|
| 1 | Read-Only MVP Foundation | Deliver the first safe local MVP: context lock, read-only backend, status dashboard, and built-in verification | PROJ-01, PROJ-02, PROJ-03, RUN-01, RUN-02, RUN-03, RUN-04, API-01, API-02, API-03, API-04, UI-01, UI-02, UI-03, UI-04, SEC-01, SEC-02, SEC-03, SEC-04 | yes |
| 2 | Verified Logs Viewer | Add bounded Hermes log display only after actual log paths and redaction rules are verified | LOGS-01, LOGS-02, LOGS-03 | yes |
| 3 | Verified Service Actions | Add start, stop, and restart controls only after launchctl commands are verified and audit logging is planned | ACT-01, ACT-02, ACT-03, ACT-04 | yes |
| 4 | Operations Enrichment | Add richer operational views for Cloudflare Tunnel, launchctl, Docker, and adjacent services where relevant | OPS-01, OPS-02, OPS-03 | yes |

## Phase 1: Read-Only MVP Foundation

**Goal:** Deliver the first safe local MVP: context lock, read-only backend, status dashboard, and built-in verification.

**Requirements:** PROJ-01, PROJ-02, PROJ-03, RUN-01, RUN-02, RUN-03, RUN-04, API-01, API-02, API-03, API-04, UI-01, UI-02, UI-03, UI-04, SEC-01, SEC-02, SEC-03, SEC-04

**Success criteria:**
1. `docs/notion/` is referenced as authoritative source context in planning docs.
2. MVP boundaries are explicit: read-only first, no free terminal, no arbitrary command execution.
3. Start/stop/restart are documented as gated until `launchctl` commands and log paths are verified.
4. Backend starts on `127.0.0.1:8787` by default.
5. `GET /api/status`, `GET /api/system`, and `GET /api/hermes/status` return structured JSON and fail safely.
6. Dashboard shows service, Bob/system, and Hermes read-only status.
7. No start, stop, restart, log-view, free-terminal, or user-defined shell endpoints exist.
8. README and `docs/security/README.md` describe local run instructions and security boundaries.
9. Verification confirms `.env` is not committed and `ALLOW_UNSAFE_COMMANDS=false`.

**Suggested plans:**
- Lock context, state, and safety rules.
- Implement read-only FastAPI MVP.
- Verify endpoints, local binding, and security boundaries.

## Phase 2: Verified Logs Viewer

**Goal:** Add bounded Hermes log display only after actual log paths and redaction rules are verified.

**Requirements:** LOGS-01, LOGS-02, LOGS-03

**Success criteria:**
1. Actual Hermes log path is verified on Bob.
2. Log output is bounded by a safe line limit.
3. Log output is sanitized before display.
4. No raw environment or credential output is exposed.

**Suggested plans:**
- Verify log paths.
- Define redaction rules.
- Implement bounded read-only log endpoint and UI panel.

## Phase 3: Verified Service Actions

**Goal:** Add start, stop, and restart controls only after launchctl commands are verified and audit logging is planned.

**Requirements:** ACT-01, ACT-02, ACT-03, ACT-04

**Success criteria:**
1. Exact launchctl commands are verified against the Bob plist and runtime.
2. Write actions require explicit confirmation.
3. Write actions are allowlisted, audited, and never user-defined.
4. Failed write actions return safe structured errors.

**Suggested plans:**
- Verify launchctl commands.
- Design confirmation and audit model.
- Implement approved service actions.

## Phase 4: Operations Enrichment

**Goal:** Add richer operational views for Cloudflare Tunnel, launchctl, Docker, and adjacent services where relevant.

**Requirements:** OPS-01, OPS-02, OPS-03

**Success criteria:**
1. Cloudflare Tunnel status is displayed only after tunnel identity is known.
2. LaunchAgent detail display uses verified label/plist values.
3. Docker status is added only if Docker becomes relevant to Hermes or adjacent services.

**Suggested plans:**
- Verify operational sources.
- Add read-only operational status cards.
- Re-run security boundary checks.

## Deferred Phases

These are intentionally outside the first read-only MVP:

- Verified logs viewer after log paths and redaction rules are confirmed.
- Start/stop/restart controls after launchctl commands are verified.
- Audit logging for write actions.
- Rich operational views for Cloudflare Tunnel, launchctl, Docker, and LM Studio.

## Coverage Validation

| Requirement Group | Count | Covered |
|-------------------|-------|---------|
| Project Grounding | 3 | 3 |
| Runtime | 4 | 4 |
| Read-Only API | 4 | 4 |
| Dashboard | 4 | 4 |
| Security | 4 | 4 |

All 19 v1 requirements are mapped to Phase 1 for the first safe read-only MVP.

---
*Roadmap created: 2026-06-03*
