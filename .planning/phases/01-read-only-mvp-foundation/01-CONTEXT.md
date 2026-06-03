# Phase 1: Read-Only MVP Foundation - Context

**Gathered:** 2026-06-03
**Status:** Ready for planning and execution
**Mode:** Manual inline GSD because `gsd-sdk` is unavailable in the shell

<domain>

## Phase Boundary

Phase 1 delivers the first safe read-only MVP foundation for Hermes UI for Bob. It locks the project safety contract, implements a local FastAPI backend on `127.0.0.1:8787`, exposes only `GET /api/status`, `GET /api/system`, and `GET /api/hermes/status`, provides a simple dashboard/root page, and verifies that no write actions, shell endpoints, secrets, or unsafe commands exist.

Start, stop, restart, log viewing, direct Cloudflare configuration, Docker setup, and free terminal access are outside this phase.

</domain>

<decisions>

## Implementation Decisions

### Scope Lock

- **D-01:** Phase 1 includes the read-only MVP foundation, not only planning setup.
- **D-02:** v1 endpoints are limited to `GET /api/status`, `GET /api/system`, and `GET /api/hermes/status`.
- **D-03:** No start, stop, restart, log-view, free-terminal, or user-defined shell endpoints may be implemented.

### Backend Approach

- **D-04:** Use Python with FastAPI and Uvicorn as the simplest stable API-first backend.
- **D-05:** Configuration is read from environment variables with safe defaults matching `.env.example`.
- **D-06:** The backend default host and port are `127.0.0.1` and `8787`.

### Hermes Status

- **D-07:** Hermes status must be read-only and fail safely if Hermes cannot be checked.
- **D-08:** Hermes status may inspect fixed launchctl/process information, but must not execute user-provided commands.
- **D-09:** If `launchctl` is unavailable or Hermes is not found, the endpoint returns `running=false` with a safe status message instead of failing the whole API.

### Dashboard

- **D-10:** The dashboard is a simple built-in root page, not a separate frontend app yet.
- **D-11:** The page displays status from the three read-only endpoints and explains that service controls are intentionally unavailable.

### Verification

- **D-12:** Verification must explicitly check endpoint behavior, local binding, absence of write-action routes, absence of arbitrary shell command surfaces, `.env` safety, and `ALLOW_UNSAFE_COMMANDS=false`.
- **D-13:** Verification fixes, if needed, must be scoped only to making the read-only MVP pass.

### Claude's Discretion

- Exact dashboard styling, internal module names, and JSON field ordering are open to straightforward implementation choices as long as the safety contract holds.

</decisions>

<specifics>

## Specific Ideas

- The UI should feel like a calm operations dashboard, not a chat app or terminal.
- Start/stop/restart should remain absent or clearly marked as unavailable until verified in a later phase.
- `.env.example` is the reference template; no real `.env` content should be created or committed.

</specifics>

<canonical_refs>

## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project State

- `README.md` - Current project summary and read-only MVP framing.
- `.env.example` - Environment variable template and `ALLOW_UNSAFE_COMMANDS=false`.
- `.planning/PROJECT.md` - Project vision, constraints, and key decisions.
- `.planning/REQUIREMENTS.md` - v1 requirements and v2/deferred scope.
- `.planning/ROADMAP.md` - Phase structure and success criteria.
- `.planning/STATE.md` - Current project memory and open gates.
- `.cursor/rules/gsd-hermes-ui.mdc` - Persistent Cursor/GSD safety rules.

### Research

- `.planning/research/STACK.md` - Stack recommendation.
- `.planning/research/FEATURES.md` - Table stakes, deferred features, and anti-features.
- `.planning/research/ARCHITECTURE.md` - Architecture and build order.
- `.planning/research/PITFALLS.md` - Critical risks and prevention.
- `.planning/research/SUMMARY.md` - Consolidated planning implications.

### Notion Source Context

- `docs/notion/01 Kravspesifikasjon MVP 374811e3522c81378221e68d872a6962.md` - Original MVP requirements; superseded for v1 where it included write actions.
- `docs/notion/02 UI-wireframes 374811e3522c8141b68fd87c75eef1e9.md` - Dashboard layout inspiration.
- `docs/notion/03 Teknisk arkitektur 374811e3522c8187a703c96665d94702.md` - Local binding, Cloudflare, and API architecture.
- `docs/notion/04 API-spesifikasjon 374811e3522c81b89dccf3d7b1b0ab4c.md` - Endpoint shape and security notes.
- `docs/notion/05 GSD-prosjektplan 374811e3522c813f99b2fa8b657798b2.md` - Original GSD master flow.
- `docs/notion/06 Cursor-regler for prosjektet 374811e3522c8154b348f5d73d1b0021.md` - Cursor/project rules.
- `docs/notion/07 Bob Mac Mini M4 – eksisterende oppsett og avhen 374811e3522c81ee802ef196c9f1d68d.md` - Bob server context.
- `docs/notion/08 Dette trenger Truls å finne frem 374811e3522c8193a2a8dac18245eae5.md` - Current Bob/Hermes details and unverified launchctl/log info.
- `docs/notion/09 env example for Hermes UI 374811e3522c8124affcf41b98c3e667.md` - Environment template guidance.
- `docs/notion/Hermes UI for Bob – grafisk brukergrensesnitt via  374811e3522c8159aaaad3eb9e89a568.md` - Overall product framing.

</canonical_refs>

<code_context>

## Existing Code Insights

### Reusable Assets

- `README.md` already states the read-only MVP direction.
- `.env.example` already contains host/port and `ALLOW_UNSAFE_COMMANDS=false`.
- `.gitignore` already ignores `.env`, `.env.local`, `.env.*.local`, key files, Cloudflare JSON, Python caches, and logs.

### Established Patterns

- No application code exists yet, so this phase should create the smallest coherent Python backend structure.
- `backend/`, `frontend/`, and `scripts/` directories exist but are empty.

### Integration Points

- New backend code should live in `backend/`.
- The built-in dashboard can be served from FastAPI root for this phase.
- `requirements.txt` is enough for this small Python backend.

</code_context>

<deferred>

## Deferred Ideas

- Hermes log viewing - Phase 2 after log path verification and redaction rules.
- Hermes start/stop/restart - Phase 3 after launchctl command verification and audit plan.
- Direct Cloudflare Tunnel configuration - later setup/verification, without credentials in repo.
- Docker - not needed for Phase 1.

</deferred>

---

*Phase: 01-read-only-mvp-foundation*
*Context gathered: 2026-06-03*
