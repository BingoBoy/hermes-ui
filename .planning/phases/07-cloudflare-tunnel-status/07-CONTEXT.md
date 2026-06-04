# Phase 7: Cloudflare Tunnel Status - Context

**Gathered:** 2026-06-04  
**Status:** Ready for planning  
**Milestone:** v1.1 Operational Visibility  
**Requirements:** OPS-01, OPS-02, OPS-03, SEC-01, SEC-02

<domain>

## Phase Boundary

Add **read-only** Cloudflare Tunnel / `cloudflared` visibility for the Hermes UI public route on Bob. Extend the existing Phase 6 operations surface (`GET /api/operations` + dashboard «Drift og tjenester») — do **not** create a parallel ops stack.

**In scope:** Local, allowlisted inspection on Bob; safe JSON for UI; tests and Bob preflight.

**Out of scope:** Write actions; tunnel start/stop/restart; Cloudflare API with tokens; reading `~/.cloudflared/*.json` or `cert.pem`; `cloudflared tunnel login`; 5B; LM Studio/n8n; Bob worker `hermes-assignee`; new POST routes.

</domain>

<decisions>

## Implementation Decisions

### D-01: Safest data sources on Bob (locked)

Use the same discipline as `backend/status.py` and `backend/operations.py`: fixed argv, `_run_read_only`, no `shell=True`, short timeouts.

| Source | Use? | Rationale |
|--------|------|-----------|
| `which cloudflared` + `cloudflared --version` | **Yes** | Binary presence and version string only |
| `pgrep -lf cloudflared` or `ps` with fixed pattern | **Yes** | Process running without parsing user config |
| Loopback `curl` to `http://127.0.0.1:8787/api/status` | **Optional / redundant** | Hermes UI already running if API responds; skip duplicate unless plan wants explicit local_ok flag |
| External `curl -sS -D - -o /dev/null` to public hostname | **Yes (metadata only)** | Proves edge path; expect HTTP 302 without Access cookie — store **status code + redirect host**, not body |
| `launchctl list` / `launchctl print` for cloudflared | **Only if Bob preflight finds a stable label** | Phase 4 tunnel is Cloudflare-managed/token-based; may not be a user LaunchAgent — verify before coding |
| `cloudflared tunnel list` / `tunnel info` | **No** | Requires origin `cert.pem` on Bob (known fail from Phase 4 discuss) |
| Read plist under `~/.cloudflared/` | **No** | Credential and config leakage risk |
| Cloudflare REST/API with API tokens | **No** | Secrets in env; out of MVP security model |

**Bob preflight (required in plan before code):**

```bash
which cloudflared
cloudflared --version
pgrep -lf cloudflared || true
# If launchd job exists:
launchctl list | grep -i cloudflared || true
curl -sS -D - -o /dev/null https://hermes-ui.strategistudio.no/api/status | head -20
```

### D-02: API shape — extend `/api/operations` (locked)

Add a top-level key `cloudflare_tunnel` (name can be `tunnel` in JSON if shorter) to the existing `get_operations_status()` response. **No new route** unless integration tests become awkward (default: extend operations).

Rationale:

- Phase 6 already owns «Drift og tjenester» and `renderOperations()`.
- One read-only GET keeps allowlist tests simple (`test_api.py` route count unchanged).
- OPS-01 requirement is “display in dashboard”, not “new microservice”.

### D-03: Safe fields for API and UI (locked)

**May expose:**

- `public_hostname` — from settings default `hermes-ui.strategistudio.no` (override via `HERMES_PUBLIC_HOSTNAME` env, not secret).
- `tunnel_name` — from settings default `bob-mac-mini-m4` (override via `HERMES_CLOUDFLARE_TUNNEL_NAME`, documented in deployment.md).
- `service_target` — constant `http://127.0.0.1:8787`.
- `cloudflared.installed`, `cloudflared.version`, `cloudflared.process_running`, optional `cloudflared.process_summary` (truncated pgrep line, no paths under `.cloudflared`).
- `edge_probe.http_status`, `edge_probe.access_redirect` (boolean: 302 to `*.cloudflareaccess.com` or similar), `edge_probe.error` if curl fails.
- `launchctl` subsection — only if label verified; same shape as launch_agents lite (state, running), **no env values**.
- `checked_at` — reuse operations-level timestamp or per-section.

**Must not expose:**

- Tunnel credential JSON, tokens, `cert.pem` paths content, org/account IDs from Cloudflare API.
- Full `cloudflared` config file paths that reveal home directory secrets (process summary may show binary path only).
- Access policy secrets, service tokens, or response bodies from external curl.

### D-04: Dashboard UX (locked)

Extend **existing** «Drift og tjeneter» / `operations-section`:

- Sub-block **«Cloudflare Tunnel»** below LaunchAgents (or after gateway card).
- Plain-language labels: Offentlig URL, Tunnel-navn, cloudflared-prosess, Edge-sjekk (HTTP-kode).
- Degrade gracefully: show `unknown` / `not_checked` when probe fails; no raw stderr dumps in UI (log server-side if needed).

No new write buttons. No tunnel controls.

### D-05: Configuration (locked)

Add to `Settings` / `.env.example` (non-secret defaults only):

- `HERMES_PUBLIC_HOSTNAME` (default `hermes-ui.strategistudio.no`)
- `HERMES_CLOUDFLARE_TUNNEL_NAME` (default `bob-mac-mini-m4`)
- Optional `HERMES_OPS_EDGE_PROBE=true` (default true on Bob) to allow disabling external curl in dev/tests.

### D-06: Tests (locked)

| Test | Purpose |
|------|---------|
| Extend `tests/test_operations.py` | `cloudflare_tunnel` key present; `read_only` still true |
| Mock `_run_read_only` / subprocess for version, pgrep, curl | No real network in CI |
| `tests/test_api.py` | Still only existing GET routes + 2 POST; operations payload shape |
| Security grep | No `shell=True`, no new routes |
| Bob manual | After deploy: `/api/operations` shows tunnel block; dashboard renders |

### D-07: Security boundaries (locked)

- Reuse `_run_read_only` from `backend/status.py` (import shared helper or move to small `backend/command_runner.py` only if plan justifies — prefer import from status to minimize diff).
- Allowlisted subcommands only: `cloudflared --version`, `/usr/bin/pgrep`, `/usr/bin/curl` with fixed URL from settings.
- External curl: max redirects 0 or 1, timeout ≤ 5s, `-o /dev/null`, no cookie jar, no `-H` with secrets.
- Fail closed: on any probe error, return structured error string, never partial file reads from `.cloudflared`.

### Claude's Discretion

- Exact JSON field names and Norwegian UI copy.
- Whether to include launchctl block after Bob preflight (omit if no label found).
- Whether edge probe runs on every request or is cheap enough (default: every request with timeout; optimize later if needed).

</decisions>

<specifics>

## Specific Ideas

- Simplest verifiable story: “cloudflared binary exists + process running + public URL returns 302 to Access” = tunnel path healthy enough for ops.
- Do not chase full tunnel connector diagnostics (QUIC details, connector ID) in v1.1.
- Align copy with Phase 4 outcome: `bob-mac-mini-m4`, `hermes-ui.strategistudio.no`.

</specifics>

<canonical_refs>

## Canonical References

### Cloudflare deployment
- `docs/architecture/deployment.md` — Public URL, tunnel name, Access flow, unauthenticated curl expectation
- `docs/architecture/cloudflare.md` — Full Phase 4 deployment (if present)
- `.planning/phases/04-cloudflare-access-tunnel/04-CONTEXT.md` — D-03–D-31 locked decisions; **avoid** `tunnel list` without cert

### Operations pattern (Phase 6)
- `backend/operations.py` — `get_operations_status`, plist/launchctl/docker patterns
- `backend/dashboard.py` — `renderOperations`, `#operations-section`
- `backend/main.py` — `GET /api/operations`
- `tests/test_operations.py`

### Requirements
- `.planning/REQUIREMENTS.md` — OPS-01–03

</canonical_refs>

<code_context>

## Existing Code Insights

### Reusable Assets
- `_run_read_only` in `backend/status.py` — subprocess discipline
- `get_operations_status()` + dashboard `renderOperations()` — extend in place
- Phase 4 documented curl probe for 302 — reuse as edge check spec

### Gaps
- No `cloudflared` settings fields yet in `backend/config.py`
- No tunnel section in operations payload or dashboard HTML/JS

### Avoid
- New `backend/tunnel_ops.py` unless planner keeps functions < ~80 lines in `operations.py`
- Duplicating LaunchAgent card UI for cloudflared without verified label

</code_context>

<deferred>

## Deferred

- `cloudflared tunnel list` after `cert.pem` exists on Bob — not v1.1
- Cloudflare Dashboard API integration — v2+
- Tunnel start/stop/restart — 5B / v2
- LM Studio, n8n, Docker tunnel routes — OPS-ADJ backlog

</deferred>
