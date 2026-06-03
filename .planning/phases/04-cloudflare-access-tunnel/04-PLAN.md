# Phase 4: Cloudflare Access and Tunnel - Plan

**Created:** 2026-06-03
**Status:** Planned — execution deferred
**Scope:** Documentation and GSD planning only — no Cloudflare or backend changes

## Goal

Plan and document secure external exposure of Hermes UI through Cloudflare Tunnel and Cloudflare Access while keeping the backend bound to `127.0.0.1:8787`.

## Recommended Target

| Item | Recommendation |
|------|----------------|
| Public URL | `https://hermes.strategistudio.no` |
| Fallback URL | `https://hermes-ui.strategistudio.no` |
| Tunnel name | `mac-mini-m4-tunnel` |
| Ingress service | `http://127.0.0.1:8787` |
| Access policy | `Only Truls` pattern in Cloudflare Zero Trust |

## Atomic Tasks

### Task 1 - Map Cloudflare Preconditions

**Output:**
- `.planning/phases/04-cloudflare-access-tunnel/04-CONTEXT.md`
- `.planning/phases/04-cloudflare-access-tunnel/04-DISCUSSION-LOG.md`

**Acceptance criteria:**
- Domain, tunnel history, Access pattern, and Bob `cloudflared` availability are documented.
- Legacy tunnel `kokebok-web` is explicitly excluded for Hermes UI routing.
- No secrets are copied into planning artifacts.

### Task 2 - Write Cloudflare Architecture Plan

**Output:**
- `docs/architecture/cloudflare.md`
- Updated `docs/architecture/deployment.md`
- Updated `docs/security/README.md`

**Acceptance criteria:**
- Documents subdomain choice, tunnel name, ingress rule, Access policy, and verification sequence.
- Includes concrete terminal commands for manual execution.
- States that commands must not be run automatically during this docs-only phase.

### Task 3 - Update GSD State and Verify

**Output:**
- Updated `.planning/STATE.md`
- Updated `.planning/ROADMAP.md`
- This plan file

**Acceptance criteria:**
- Phase 4 marked as planned, not executed.
- Verification confirms docs-only diff, no secrets added, pytest still passes.
- Next step clearly points to manual Cloudflare execution.

## Manual Execution Sequence (Next Step)

Run on Bob as `trulsdahl`. Do not commit outputs that contain secrets.

### Step 0 - Preconditions

```bash
# Confirm Hermes UI is healthy locally
curl -s http://127.0.0.1:8787/api/status | python3 -m json.tool
lsof -nP -iTCP:8787 -sTCP:LISTEN

# Confirm cloudflared is available
/opt/homebrew/bin/cloudflared --version
```

### Step 1 - Authenticate cloudflared for tunnel management

```bash
/opt/homebrew/bin/cloudflared tunnel login
/opt/homebrew/bin/cloudflared tunnel list
/opt/homebrew/bin/cloudflared tunnel info mac-mini-m4-tunnel
```

If the tunnel does not exist yet:

```bash
/opt/homebrew/bin/cloudflared tunnel create mac-mini-m4-tunnel
/opt/homebrew/bin/cloudflared tunnel list
/opt/homebrew/bin/cloudflared tunnel info mac-mini-m4-tunnel
```

### Step 2 - Create Cloudflare Access application and policy

In Cloudflare Zero Trust dashboard:

1. Create an application for `hermes.strategistudio.no`.
2. Add an Access policy equivalent to existing internal `Only Truls` apps.
3. Verify unauthenticated requests receive the Access login page.

Do not store Access tokens or service tokens in git or Notion.

### Step 3 - Add DNS route and ingress

```bash
/opt/homebrew/bin/cloudflared tunnel route dns mac-mini-m4-tunnel hermes.strategistudio.no
```

Example ingress config fragment for Bob-local `config.yml`:

```yaml
tunnel: mac-mini-m4-tunnel
credentials-file: /Users/trulsdahl/.cloudflared/<TUNNEL-UUID>.json

ingress:
  - hostname: hermes.strategistudio.no
    service: http://127.0.0.1:8787
  - service: http_status:404
```

Then run the tunnel:

```bash
/opt/homebrew/bin/cloudflared tunnel --config ~/.cloudflared/config.yml run mac-mini-m4-tunnel
```

For persistence, install a LaunchAgent or `cloudflared service install` after the config is verified.

### Step 4 - Local verification on Bob

```bash
curl -s http://127.0.0.1:8787/api/status
curl -s http://127.0.0.1:8787/api/system
curl -s http://127.0.0.1:8787/api/logs/sources
```

Expected: JSON success responses with `read_only: true`.

### Step 5 - External verification after Access

From MacBook or phone off local network:

1. Open `https://hermes.strategistudio.no`
2. Confirm Cloudflare Access login appears first.
3. After login, confirm Hermes UI dashboard loads.
4. Confirm API read-only behavior still holds.

Optional CLI check from an authenticated session:

```bash
curl -I https://hermes.strategistudio.no/api/status
```

Unauthenticated requests should not reach Hermes UI directly.

## Security Checklist

- [ ] Cloudflare Access active before sharing URL
- [ ] Ingress points only to `http://127.0.0.1:8787`
- [ ] Backend still bound to `127.0.0.1`
- [ ] No router port forwarding added
- [ ] No Cloudflare credentials committed
- [ ] No Access tokens stored in repo or Notion
- [ ] `ALLOW_UNSAFE_COMMANDS=false` unchanged

## Completion Criteria for This Docs Phase

- Planning docs written and GSD state updated
- No Cloudflare configuration changed
- No backend code changed
- Verification passed

*Plan created: 2026-06-03*
