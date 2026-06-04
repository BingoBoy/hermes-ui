# Phase 6: Operations Enrichment — Context

**Created:** 2026-06-04  
**Roadmap:** Phase 6 (top-level) — distinct from decimal phases 6A–6N (v2.1-bob-ux, shipped).

## Goal

Add richer **read-only** operational views for LaunchAgents and adjacent services on Bob, without new write actions or client-controlled commands.

## Requirements

- **OPS-02:** LaunchAgent details displayed when plist and label are verified.
- **OPS-03:** Docker status only if Docker is relevant to Hermes or adjacent services.

**Out of scope for this phase:**

- **OPS-01** Cloudflare Tunnel UI (documented in Phase 4; no new tunnel status card required here).
- Start/stop LaunchAgents (Phase 5B still blocked).
- Hermes UI self-restart from dashboard.
- Free terminal or arbitrary command execution.
- Exposing plist `EnvironmentVariables` values (names-only or omit).

## Locked decisions

| Topic | Decision |
|-------|----------|
| API shape | New `GET /api/operations` returning structured JSON (keep `/api/system` and `/api/hermes/status` unchanged for regression). |
| Command discipline | Fixed argv via `_run_read_only` / existing patterns; `shell=False`; no client paths or labels. |
| LaunchAgent scope | Two verified jobs: `no.truls.hermes-ui` and `ai.hermes.gateway` (paths from server config / documented defaults). |
| Plist inspection | Server-side `plistlib` read of allowlisted plist paths only; return label, program summary, stdout/stderr log paths — **never** secret values. |
| Docker | Off by default (`HERMES_OPS_INCLUDE_DOCKER=false`); enable only after Bob verify documents relevance. |
| Dashboard | New read-only section **«Drift og tjenester»** after Bob blocks, before existing status cards (preserve `test_dashboard_orders_bob_communication_before_operations`). |
| Deploy | Bob fast-forward pull + LaunchAgent restart only if backend/env changes; no Cloudflare changes. |

## Verified sources (pre-research)

From `docs/architecture/deployment.md` and README (Bob, 2026-06-03/04):

| Service | Label | Plist |
|---------|-------|-------|
| Hermes UI | `no.truls.hermes-ui` | `~/Library/LaunchAgents/no.truls.hermes-ui.plist` |
| Hermes gateway | `ai.hermes.gateway` | `~/Library/LaunchAgents/ai.hermes.gateway.plist` |

Gateway process is **not** Docker-backed per Notion/deployment notes.

## Dependencies

- Phases 1–4.5 (read-only API + dashboard).
- Phase 5A (restart gateway — unchanged).
- v2.1-bob-ux (Bob sections ordering — must not regress).

## Success criteria (from ROADMAP)

1. LaunchAgent detail display uses verified label/plist values.
2. Docker status added only if relevant on Bob.
3. Operational views remain read-only.
