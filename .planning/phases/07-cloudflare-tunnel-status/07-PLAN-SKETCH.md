# Phase 7 Plan Sketch (for `/gsd-plan-phase 7`)

**Not executable** — input to planner. Expand into formal `07-PLAN.md` with verification tasks.

## Wave 0: Bob preflight (discuss gate → plan doc)

Run on Bob, record in plan:

```bash
which cloudflared && cloudflared --version
pgrep -lf cloudflared || echo "no process"
launchctl list 2>/dev/null | grep -i cloudflared || echo "no launchd label"
curl -sS -D - -o /dev/null --max-time 5 https://hermes-ui.strategistudio.no/api/status 2>&1 | head -15
```

Decide: include launchctl block yes/no.

## Wave 1: Config + backend

- `backend/config.py`: `hermes_public_hostname`, `hermes_cloudflare_tunnel_name`, `hermes_ops_edge_probe` (defaults from deployment.md).
- `backend/operations.py`: `def _cloudflare_tunnel_status(settings) -> dict` using `_run_read_only` from `status`.
- Merge into `get_operations_status()` as `"cloudflare_tunnel": {...}`.
- `.env.example` + `docs/architecture/deployment.md` one paragraph.

## Wave 2: Dashboard

- `backend/dashboard.py`: in `renderOperations`, render tunnel card (Norwegian labels, no secrets).
- Order: after launch agents, before docker block.

## Wave 3: Tests + verify

- `tests/test_operations.py`: shape, mocks, edge 302 case.
- `tests/test_api.py`: unchanged route count.
- Bob: curl `/api/operations`, confirm keys; no restart unless code changed.

## Success criteria (from ROADMAP)

- OPS-01–03 satisfied
- SEC-01–02 unchanged
- No new POST routes

## Estimated scope

~3 plan tasks, 1 wave execute, docs-only Bob preflight can be task 0.
