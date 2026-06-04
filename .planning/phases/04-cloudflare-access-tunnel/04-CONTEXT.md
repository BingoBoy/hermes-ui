# Phase 4: Cloudflare Access and Tunnel - Context

**Gathered:** 2026-06-03
**Executed:** 2026-06-04
**Status:** Complete
**Scope:** Cloudflare deployment verified and documented

<domain>

## Phase Boundary

Phase 4 plans how Hermes UI on Bob should be exposed through Cloudflare Tunnel and Cloudflare Access. This phase verifies current Cloudflare preconditions, chooses hostname and tunnel naming, documents ingress and Access policy requirements, and records manual execution commands. It does not configure Cloudflare, does not modify backend code, does not bind to `0.0.0.0`, and does not open router ports.

</domain>

<decisions>

## Implementation Decisions

### Verified Preconditions

- **D-01:** Hermes UI runs on Bob as LaunchAgent `no.truls.hermes-ui` on `127.0.0.1:8787`.
- **D-02:** API reports `read_only: true` and `allow_unsafe_commands: false`.
- **D-03:** `cloudflared` is installed on Bob at `/opt/homebrew/bin/cloudflared` (version `2026.5.1`).
- **D-04:** Cloudflare Zero Trust is used for `strategistudio.no`.
- **D-05:** Existing Bob SSH external access uses Cloudflare Access at `bob-ssh.strategistudio.no`.
- **D-06:** `cloudflared tunnel list` currently fails on Bob until an origin certificate is configured via `cloudflared tunnel login`.

### Recommended Public Identity

- **D-07:** Recommended public hostname: `https://hermes.strategistudio.no`
- **D-08:** Documented fallback hostname: `https://hermes-ui.strategistudio.no`
- **D-09:** Recommended dedicated tunnel name: `mac-mini-m4-tunnel`
- **D-10:** Do not route Hermes UI through the legacy shared tunnel `kokebok-web`.

### Ingress and Binding

- **D-11:** Tunnel ingress must target `http://127.0.0.1:8787` only.
- **D-12:** Hermes UI backend must remain bound to `127.0.0.1`, never `0.0.0.0`.
- **D-13:** No router port forwarding is required or allowed for this design.

### Access Policy

- **D-14:** Cloudflare Access must be active before the public URL is used.
- **D-15:** Recommended policy pattern: allow only Truls, matching existing internal app policy style (`Only Truls`).
- **D-16:** Session duration, identity provider, and MFA should follow existing Zero Trust defaults for internal apps.

### Secrets Handling

- **D-17:** Tunnel credential JSON files stay in `~/.cloudflared/` on Bob only.
- **D-18:** `.env.example` remains a template; real `.env` stays local and uncommitted.
- **D-19:** Do not store Access service tokens, tunnel tokens, or org tokens in git, Notion, or repo docs.
- **D-20:** Documentation may reference file locations and command patterns, not secret values.

### Safety Boundaries

- **D-21:** No write actions, free terminal, or shell-command routes may be added while planning Cloudflare exposure.
- **D-22:** External exposure does not change the read-only MVP contract.
- **D-23:** Logs API remains bounded and redacted; tunnel exposure does not widen filesystem access.

### Actual Deployment Outcome

- **D-24:** Public hostname in use: `https://hermes-ui.strategistudio.no`
- **D-25:** Existing tunnel `bob-mac-mini-m4` was reused; no new tunnel was created.
- **D-26:** Route was added as a Published application route in Cloudflare Dashboard.
- **D-27:** Service target is `http://127.0.0.1:8787`.
- **D-28:** No Bob-local ingress `config.yml` was created.
- **D-29:** Tunnel remains token-based and Cloudflare-managed.
- **D-30:** Cloudflare Access self-hosted application is active with `Only Truls` policy.
- **D-31:** Unauthenticated external requests receive HTTP `302` to Cloudflare Access login.

</decisions>

<specifics>

## Specific Ideas

- Use a dedicated Bob Mac Mini M4 tunnel rather than adding Hermes UI to an unrelated legacy ingress file.
- Keep local smoke tests on Bob (`curl http://127.0.0.1:8787/api/status`) as the first gate before any external test.
- External browser test should expect a Cloudflare Access login page before Hermes UI loads.
- After execution, set `HERMES_UI_PUBLIC_URL=https://hermes.strategistudio.no` locally on Bob only.

</specifics>

<canonical_refs>

## Canonical References

**Downstream agents MUST read these before executing Cloudflare setup.**

### Project State

- `.planning/STATE.md`
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md` — `OPS-01`, `SEC-04`
- `docs/architecture/deployment.md`
- `docs/architecture/cloudflare.md`
- `docs/security/README.md`

### Notion Context

- `docs/notion/08 Dette trenger Truls å finne frem...` — domain, tunnel history, subdomain options
- `docs/notion/07 Bob Mac Mini M4 – eksisterende oppsett...` — tunnel naming guidance
- `docs/notion/Hermes UI for Bob – grafisk brukergrensesnitt via Cloudflare` — target architecture

### Current Runtime

- Hermes UI LaunchAgent: `no.truls.hermes-ui`
- Local URL: `http://127.0.0.1:8787`
- Read-only API surface in `backend/main.py`

</canonical_refs>

<open_questions>

## Open Questions for Execution

1. Confirm `hermes.strategistudio.no` is unused in Cloudflare DNS before routing.
2. Decide whether to create a new tunnel or reuse an existing inactive `macmini-tunnel` after inspecting `cloudflared tunnel list` post-login.
3. Choose LaunchAgent vs manual `cloudflared service install` for persistent tunnel process on Bob.
4. Confirm whether `HERMES_UI_PUBLIC_URL` should be added to Bob `.env` and LaunchAgent environment after go-live.

</open_questions>

---

*Context gathered: 2026-06-03*
