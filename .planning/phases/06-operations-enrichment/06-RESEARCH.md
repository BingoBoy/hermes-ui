# Phase 6: Operations Enrichment — Research

**Date:** 2026-06-04

## Existing patterns

| Area | Location | Notes |
|------|----------|-------|
| Read-only subprocess | `backend/status.py` `_run_read_only` | `launchctl list`, `ps`, `vm_stat`, `uptime` — 2s timeout, no shell |
| Hermes gateway status | `get_hermes_status` | Uses `HERMES_LAUNCHD_LABEL` + process grep |
| Service restart | `backend/service_actions.py` | Fixed `launchctl kickstart` argv only |
| Dashboard layout | `backend/dashboard.py` | Bob Inbox → Send → History → Statuskort → Logger |
| Route allowlist tests | `tests/test_api.py` | Guards against new write/terminal routes |

## OPS-02 — LaunchAgent details

**Already in API (partial):**

- `/api/hermes/status` returns `launchd_label`, `launchctl` line match, process hints.
- Missing: plist path, log paths, program summary, Hermes UI LaunchAgent card, `launchctl print` state details.

**Safe enrichment approach:**

1. Add `Settings` fields for allowlisted plist paths and labels (defaults match `deployment.md`).
2. `plistlib.readPlist` on those paths only — extract non-secret fields.
3. Optional `launchctl print gui/{uid}/{label}` with label from settings (same discipline as service-actions doc).
4. Merge with existing `_launchctl_status(label)` for running/pid.

**Bob verify before implement:**

```bash
launchctl print gui/$(id -u)/no.truls.hermes-ui
launchctl print gui/$(id -u)/ai.hermes.gateway
plutil -p ~/Library/LaunchAgents/no.truls.hermes-ui.plist
plutil -p ~/Library/LaunchAgents/ai.hermes.gateway.plist
```

## OPS-03 — Docker

**Evidence:**

- `docs/architecture/deployment.md`: gateway runs via Python LaunchAgent, not Docker.
- Notion: Docker «eventuelt senere» for adjacent services.

**Recommendation:**

- Implement optional `docker info` / `docker ps --format` behind `HERMES_OPS_INCLUDE_DOCKER=true`.
- Default **false** on Bob until verify confirms an adjacent container Hermes UI should surface (e.g. n8n).
- When false: API returns `docker: { "included": false, "reason": "disabled_by_config" }` without calling docker.

**Bob verify:**

```bash
which docker
docker ps --format '{{.Names}}' 2>/dev/null | head
```

If no Hermes-adjacent container: keep gate off; satisfy OPS-03 as «assessed, not applicable».

## API design

**`GET /api/operations`**

```json
{
  "read_only": true,
  "launch_agents": [
    {
      "id": "hermes-ui",
      "label": "no.truls.hermes-ui",
      "plist_path": "/Users/.../no.truls.hermes-ui.plist",
      "plist_readable": true,
      "program_summary": "uvicorn backend.main:app ...",
      "log_paths": { "stdout": "...", "stderr": "..." },
      "launchctl": { "matched": true, "pid": 12345 },
      "domain": "gui/501/no.truls.hermes-ui"
    }
  ],
  "docker": { "included": false },
  "checked_at": "..."
}
```

## Dashboard

- Section id: `operations-section` (or `drift-tjenester-section`).
- Insert **after** `#bob-history-section`, **before** `.grid` status cards.
- Update/add test: bob-history < operations < statuskort.
- Reuse badge/meta patterns from 4.5 status cards.

## Risks

| Risk | Mitigation |
|------|------------|
| Plist env leaks secrets | Never return env values; optional key names only |
| Unbounded docker output | Limit `docker ps` to N containers; format string fixed |
| New write routes | Single new GET; extend allowlist test |
| launchctl print slow | 2–3s timeout; degrade gracefully |

## Not doing

- Cloudflare `cloudflared` status in UI (OPS-01 deferred).
- LM Studio / n8n port probes (future backlog).
- Log viewer for hermes-ui.log (separate from OPS-02 metadata display).
