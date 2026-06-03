# Phase 4: Cloudflare Access and Tunnel - Discussion Log

> Audit trail only. Planning should use `04-CONTEXT.md` and `04-PLAN.md` as canonical input.

**Date:** 2026-06-03
**Mode:** Manual inline GSD
**Reason:** `gsd-sdk` was not available in the shell.

## Inputs Reviewed

- `README.md`
- `.env.example`
- `.planning/STATE.md`
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/phases/03-document-bob-launchagent/03-PLAN.md`
- `docs/architecture/deployment.md`
- `docs/security/README.md`
- `docs/api/logs.md`
- `docs/notion/`
- `backend/`
- `tests/`
- read-only Bob metadata via `BobRemote`

## Bob Cloudflare Preconditions Verified

| Item | Value |
|------|-------|
| `cloudflared` binary | `/opt/homebrew/bin/cloudflared` |
| `cloudflared` version | `2026.5.1` |
| Zero Trust team domain | `strategistudio.cloudflareaccess.com` (inferred from local Access token filename pattern) |
| DNS zone | `strategistudio.no` |
| Existing SSH Access host | `bob-ssh.strategistudio.no` |
| Hermes UI local bind | `127.0.0.1:8787` |
| Hermes UI LaunchAgent | `no.truls.hermes-ui` |
| `cloudflared tunnel list` on Bob | Failed: origin certificate not configured locally (`cert.pem` missing) |
| Existing migration config tunnel name | `kokebok-web` (legacy/shared tunnel — not chosen for Hermes UI) |
| Tunnel LaunchAgent on Bob | Not found |

## Decisions Captured

| Area | Decision | Rationale |
|------|----------|-----------|
| Scope | Plan and document only; do not change Cloudflare runtime | User requested docs-only phase before execution |
| Subdomain | Recommend `hermes.strategistudio.no` | Shorter public URL; matches primary Notion recommendation and product name |
| Alternate subdomain | Keep `hermes-ui.strategistudio.no` as documented fallback | Useful if `hermes` is reserved or ambiguous later |
| Tunnel name | Recommend `mac-mini-m4-tunnel` | Matches Bob server docs; separate from legacy `kokebok-web` / `n8ntunnel` |
| Ingress target | `http://127.0.0.1:8787` only | Preserves loopback binding; no router port forwarding |
| Access policy | Require Cloudflare Access before public use; mirror `Only Truls` pattern | Consistent with other internal apps on `strategistudio.no` |
| Credentials | Keep tunnel credentials and Access tokens local under `~/.cloudflared/` | Never commit JSON credentials, tokens, or `.env` values |
| Backend changes | None in this phase | Hermes UI remains read-only and locally bound |
| Execution order | Access policy first, then tunnel DNS/ingress, then external browser test | Fail closed if Access is missing |

## Deferred to Execution Phase

- `cloudflared tunnel login`
- Creating or selecting final tunnel UUID
- Writing live `config.yml` ingress for Hermes UI
- LaunchAgent/systemd service for `cloudflared`
- Cloudflare Zero Trust application and policy creation in dashboard
- Setting `HERMES_UI_PUBLIC_URL` on Bob

## Explicit Non-Actions

- No Cloudflare dashboard changes were made.
- No tunnel routes were created.
- No DNS records were added.
- No backend code was modified.
- No secrets were written to git, Notion exports, or planning docs.

---

*Discussion log written: 2026-06-03*
