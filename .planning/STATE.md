# State: Hermes UI for Bob

## Project Reference

See: `.planning/PROJECT.md` (updated 2026-06-03)

**Core value:** Truls can safely see whether Bob and Hermes are healthy without exposing shell access, secrets, or unsafe service controls.

**Current focus:** Phase 1 - Read-Only MVP Foundation

## Workflow

Use original GSD master flow:

```text
discuss -> plan -> execute -> verify
```

## Current Phase

| Field | Value |
|-------|-------|
| Phase | 1 |
| Name | Read-Only MVP Foundation |
| Status | In Progress |
| Requirements | PROJ-01, PROJ-02, PROJ-03, RUN-01, RUN-02, RUN-03, RUN-04, API-01, API-02, API-03, API-04, UI-01, UI-02, UI-03, UI-04, SEC-01, SEC-02, SEC-03, SEC-04 |
| Current command | `/gsd-discuss-phase 1` run inline because `gsd-sdk` is unavailable |
| Next command | `/gsd-verify-work` after implementation verification |

## Session Plan

Phase 1 is being executed as a complete manual GSD loop:

```text
discuss -> plan -> execute -> verify
```

Atomic tasks:

1. Lock read-only MVP scope, planning state, and safety contract.
2. Implement the FastAPI read-only backend and status dashboard.
3. Verify endpoints, local binding, secrets safety, and absence of write actions.

## Open Gates

- Verify actual Hermes launchctl commands before implementing start, stop, or restart.
- Verify actual Hermes log paths before implementing log display.
- Keep Phase 1 read-only until built-in verification passes.
- Keep real `.env` out of git.
- Keep `ALLOW_UNSAFE_COMMANDS=false`.
- Do not add Cloudflare configuration or credentials in this phase.

## Memory

- `docs/notion/` is authoritative source context.
- `127.0.0.1:8787` is the local binding target.
- Cloudflare Access is required for later external access.
- Free terminal in browser is out of scope.
- Phase 1 includes the first read-only MVP foundation, not write actions.

---
*Last updated: 2026-06-03 during Phase 1 inline GSD execution*
