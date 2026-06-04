# Project Milestones: Hermes UI for Bob

## v1: Safe Operations Dashboard (Shipped: 2026-06-04)

**Delivered:** Read-only MVP through operations enrichment — status API, bounded gateway logs, Cloudflare Access, dashboard UX, allowlisted restart and Bob kanban APIs, `GET /api/operations`.

**Phases:** 1, 2, 3, 4, 4.5, 5 (5A/5C/5D), 6 — **7 phase entries**

**Known gaps at close (tech debt, not blockers):**

- 5B gateway start/stop deferred
- OPS-01 tunnel status card not in UI
- Phases 1–5 lack formal `*-VERIFICATION.md`
- Bob worker `hermes-assignee` — external ops

**Key accomplishments:**

- FastAPI dashboard on `127.0.0.1:8787` with security boundaries
- Production URL `https://hermes-ui.strategistudio.no`
- Gateway restart + Bob task create/list/show live on Bob
- LaunchAgent operational cards (Phase 6)

**Stats:**

- Git: `c6afa4f` → `dd7e661` (63 commits on `main`)
- Tests: 77 pytest passing at close
- Audit: `tech_debt` — see `.planning/milestones/v1-MILESTONE-AUDIT.md`

**Archives:**

- Roadmap: `.planning/milestones/v1-ROADMAP.md`
- Requirements: `.planning/milestones/v1-REQUIREMENTS.md`
- Audit: `.planning/milestones/v1-MILESTONE-AUDIT.md`

**Tag:** `v1`

---

## v2.1-bob-ux: Bob Dashboard / Kanban UX (Shipped: 2026-06-04)

**Status:** Completed and archived.

**Delivered:** Safe Bob task communication in the Hermes UI dashboard — inbox, templates, results, assignee, artifacts, and queue labels on top of Phase 5C/5D APIs.

**Phases completed:** 6A–6N (14 phase entries; 6N docs-only closure)

**Archives:**

- Roadmap: `.planning/milestones/v2.1-bob-ux-ROADMAP.md`
- Requirements: `.planning/milestones/v2.1-bob-ux-REQUIREMENTS.md`
- Audit: `.planning/milestones/v2.1-bob-ux-MILESTONE-AUDIT.md`

**Tag:** `v2.1-bob-ux`

---

## What's next

Milestones **v1** and **v2.1-bob-ux** are shipped and archived. No `REQUIREMENTS.md` on disk — define the next milestone with:

```text
/gsd-new-milestone
```

Or pick backlog work via `/gsd-discuss-phase` / `/gsd-add-phase` (5B, OPS-01, UI logs).
