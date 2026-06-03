# Phase 1: Read-Only MVP Foundation - Plan

**Created:** 2026-06-03
**Status:** Complete
**Scope:** Strict read-only MVP

## Goal

Deliver the first safe local Hermes UI foundation: FastAPI backend, three read-only status endpoints, simple dashboard page, local run instructions, security notes, and built-in verification.

## Atomic Tasks

### Task 1 - Lock Planning and Safety Contract

**Output:**
- Updated `.planning/STATE.md`
- Updated `.planning/ROADMAP.md`
- Updated `.planning/REQUIREMENTS.md`
- Phase context and plan under `.planning/phases/01-read-only-mvp-foundation/`

**Acceptance criteria:**
- Phase 1 explicitly covers the read-only MVP foundation.
- Deferred write actions remain out of scope.
- GSD flow remains discuss -> plan -> execute -> verify.

### Task 2 - Implement Read-Only FastAPI MVP

**Output:**
- `backend/` FastAPI application structure
- `requirements.txt`
- `GET /api/status`
- `GET /api/system`
- `GET /api/hermes/status`
- Root dashboard page
- README local run instructions
- `docs/security/README.md`

**Acceptance criteria:**
- Backend defaults to `127.0.0.1:8787`.
- Status endpoints return structured JSON.
- Hermes status is read-only and fails safely.
- No start/stop/restart/log/free-shell/user-command endpoints exist.
- `ALLOW_UNSAFE_COMMANDS` remains false by default and in `.env.example`.

### Task 3 - Built-In Verification

**Output:**
- Syntax/type checks where available
- Local server smoke test if dependencies can be installed
- Curl verification for `/api/status`, `/api/system`, and `/api/hermes/status`
- Security checks for forbidden routes/terms and secrets indicators

**Acceptance criteria:**
- `git status` and `git log --oneline -5` checked.
- Python syntax checks pass.
- Local server starts on `127.0.0.1:8787` if environment allows.
- Curl checks pass if server starts.
- Verification confirms no write actions, free shell, user-defined command API, committed `.env`, or credentials.

## Correction Policy

If verification fails, create a correction plan with at most two atomic tasks. Fix only what is necessary for the read-only MVP to pass, then re-run verification and commit the fix separately.

## Completion

Phase 1 completed on 2026-06-03 with built-in verification passing:

- Python syntax compilation passed.
- Pytest passed.
- Local server and curl endpoint checks passed.
- Security checks confirmed no write actions or unsafe command surface.

---

*Plan created: 2026-06-03*
*Plan completed: 2026-06-03*
