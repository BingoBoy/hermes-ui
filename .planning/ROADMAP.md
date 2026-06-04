# Roadmap: Hermes UI for Bob

**Created:** 2026-06-03  
**Flow:** discuss -> plan -> execute -> verify

## Milestones

- ✅ **v1** — Safe Operations Dashboard (Phases 1–6) — shipped 2026-06-04 → [archive](milestones/v1-ROADMAP.md)
- ✅ **v2.1-bob-ux** — Bob Dashboard / Kanban UX (6A–6N) — shipped 2026-06-04 → [archive](milestones/v2.1-bob-ux-ROADMAP.md)
- **Next:** `/gsd-new-milestone` or pick from [Backlog](#backlog--not-yet-planned)

## Overview

| Phase | Milestone | Name | Status |
|-------|-----------|------|--------|
| 1–6 | v1 | Foundation → Operations | Shipped |
| 6A–6N | v2.1-bob-ux | Bob Dashboard UX | Shipped |

<details>
<summary>✅ v1 — Safe Operations Dashboard (Phases 1–6) — SHIPPED 2026-06-04</summary>

Full details: [milestones/v1-ROADMAP.md](milestones/v1-ROADMAP.md)

- [x] Phase 1: Read-Only MVP Foundation
- [x] Phase 2: Verified Logs Viewer
- [x] Phase 3: Document Bob LaunchAgent Deployment
- [x] Phase 4: Cloudflare Access and Tunnel
- [x] Phase 4.5: Dashboard UX Cleanup
- [x] Phase 5: Service actions + Bob tasks (5B deferred)
- [x] Phase 6: Operations Enrichment

Audit: [milestones/v1-MILESTONE-AUDIT.md](milestones/v1-MILESTONE-AUDIT.md)

</details>

<details>
<summary>✅ v2.1-bob-ux — Bob Dashboard / Kanban UX (Phases 6A–6N) — SHIPPED 2026-06-04</summary>

Full details: [milestones/v2.1-bob-ux-ROADMAP.md](milestones/v2.1-bob-ux-ROADMAP.md)

- [x] 6A–6B: Task follow-up + Bob Inbox
- [x] 6C–6D: Task templates + optional inputs
- [x] 6E–6I: Result actions + assignee + summary + UAT closure
- [x] 6J–6M: Layout, expand UAT, artifacts, queue hygiene
- [x] 6N: Milestone documentation cleanup

Audit: [milestones/v2.1-bob-ux-MILESTONE-AUDIT.md](milestones/v2.1-bob-ux-MILESTONE-AUDIT.md)

</details>

## Backlog / not yet planned

| Item | Notes |
|------|--------|
| **5B** Gateway start/stop | `bootstrap`/`bootout` documented; blocked until live verify in maintenance window |
| **OPS-01** Cloudflare tunnel status in UI | Tunnel/Access documented (Phase 4); no live tunnel status card yet |
| **Hermes UI LaunchAgent logs in dashboard** | Paths at `~/.hermes-ui/logs/`; not in bounded logs allowlist |
| **LM Studio / n8n** adjacent services | Notion only; no plan |
| **Bob worker `hermes-assignee`** | External Hermes Agent ops on Bob |

**Already delivered (do not replan):**

- v1 phases 1–6 and v2.1-bob-ux 6A–6N — see milestone archives above

---
*Roadmap: v1 + v2.1-bob-ux archived 2026-06-04*
