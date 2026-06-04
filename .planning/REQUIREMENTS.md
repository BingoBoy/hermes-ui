# Requirements: Hermes UI for Bob

**Defined:** 2026-06-04  
**Milestone:** v1.1 — Operational Visibility  
**Core Value:** Truls can safely see whether Bob and Hermes are healthy without exposing shell access, secrets, or unsafe service controls.

Prior milestones archived: **v1** (phases 1–6), **v2.1-bob-ux** (6A–6N). See `.planning/milestones/v1-REQUIREMENTS.md`.

## v1.1 Requirements (this milestone)

Read-only operational visibility only. No new write routes unless explicitly moved to a later gated phase.

### Cloudflare / external path

- [ ] **OPS-01**: Dashboard shows read-only Cloudflare Tunnel / `cloudflared` connectivity status for the Bob Hermes UI route (hostname, tunnel name, process/running state, last check time).
- [ ] **OPS-02**: Tunnel status uses allowlisted, fixed commands or read-only checks only — no client-supplied hostnames, tokens, or config paths.
- [ ] **OPS-03**: Tunnel status output is sanitized; no credentials, tunnel JSON, or `.cloudflared` secrets in API or UI.

### Hermes UI logs

- [ ] **LOG-UI-01**: Hermes UI LaunchAgent stdout/stderr log paths are verified on Bob and added to the server-side logs allowlist (`~/.hermes-ui/logs/` per deployment docs).
- [ ] **LOG-UI-02**: User can view bounded Hermes UI logs in the dashboard via existing `/api/logs/{source_id}` pattern (same line limits and redaction as gateway logs).
- [ ] **LOG-UI-03**: Log viewer remains read-only; no new write routes; client cannot pass arbitrary file paths.

### Regression / security (carry-forward)

- [ ] **SEC-01**: Existing allowlisted POST routes unchanged (`/api/hermes/restart`, `/api/bob/tasks` only).
- [ ] **SEC-02**: No `shell=True`, no `hermes -z`, no free terminal or arbitrary command API.

## v2 Requirements (deferred — not v1.1 roadmap)

Tracked for later milestones. Do not implement without explicit discuss/plan gates.

### Service actions (gated)

- **ACT-01**: Gateway **start** via verified `launchctl bootstrap` — requires documented maintenance window + live verify on Bob (**5B**).
- **ACT-02**: Gateway **stop** via verified `launchctl bootout` — same gate as ACT-01.

### External / adjacent ops

- **OPS-EXT-01**: Bob kanban-worker has `hermes-assignee` in PATH — **Hermes Agent ops on Bob**, not Hermes UI code; document runbook only in v1.1 unless scope expands.
- **OPS-ADJ-01**: Read-only status for adjacent services (LM Studio, n8n, Docker containers) — only after Bob verify proves relevance; not v1.1.

## Out of Scope (v1.1)

| Feature | Reason |
|---------|--------|
| Gateway start/stop in UI | 5B blocked until maintenance-window live verify — v2 |
| Free browser terminal | Permanent security exclusion |
| Arbitrary shell from API | Violates control-panel model |
| Cloudflare credential management in UI | Credentials stay in `~/.cloudflared/` on Bob |
| Full n8n / LM Studio integration | Not verified on Bob; needs product decision |
| Fixing `hermes-assignee` in worker | External to Hermes UI repo |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| OPS-01 | Phase 7 | Pending |
| OPS-02 | Phase 7 | Pending |
| OPS-03 | Phase 7 | Pending |
| LOG-UI-01 | Phase 8 | Pending |
| LOG-UI-02 | Phase 8 | Pending |
| LOG-UI-03 | Phase 8 | Pending |
| SEC-01 | Phase 7–8 | Pending |
| SEC-02 | Phase 7–8 | Pending |

**Coverage:**

- v1.1 requirements: 8 total
- Mapped to phases: 8
- Unmapped: 0

---
*Requirements defined: 2026-06-04 — milestone v1.1 Operational Visibility*
