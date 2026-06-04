# Phase 4: Cloudflare Access and Tunnel - Plan

**Created:** 2026-06-03
**Completed:** 2026-06-04
**Status:** Complete
**Scope:** Cloudflare deployment verified and documented — no backend code changes in this execution step

## Goal

Expose Hermes UI safely through Cloudflare Tunnel and Cloudflare Access while keeping the backend bound to `127.0.0.1:8787`.

## Actual Deployment

| Item | Actual value |
|------|--------------|
| Public URL | `https://hermes-ui.strategistudio.no` |
| Tunnel name | `bob-mac-mini-m4` |
| Route type | Published application route |
| Service target | `http://127.0.0.1:8787` |
| Access application | Self-hosted application |
| Access policy | `Only Truls` pattern |
| Local `config.yml` | Not created |
| New tunnel created | No |

## Atomic Tasks

### Task 1 - Configure Cloudflare Route and Access

**Status:** Complete outside repo

**Actual outcome:**
- Reused existing tunnel `bob-mac-mini-m4`
- Added Published application route to `http://127.0.0.1:8787`
- Enabled Cloudflare Access self-hosted application
- Applied `Only Truls` Access policy

### Task 2 - Verify External Protection

**Status:** Complete

**Verification:**
- Unauthenticated `curl` to `/api/status` returns HTTP `302` to Cloudflare Access login
- Local Bob bind remains `127.0.0.1:8787`
- Backend remains read-only

### Task 3 - Document Deployment and Update GSD State

**Status:** Complete

**Output:**
- Updated `docs/architecture/cloudflare.md`
- Updated `docs/architecture/deployment.md`
- Updated `docs/security/README.md`
- Updated `.planning/STATE.md`
- Updated `.planning/ROADMAP.md`
- Updated phase 4 planning artifacts

## Security Checklist

- [x] Cloudflare Access active before public use
- [x] Route points only to `http://127.0.0.1:8787`
- [x] Backend still bound to `127.0.0.1`
- [x] No router port forwarding added
- [x] No Cloudflare credentials committed
- [x] No Access tokens stored in repo or Notion
- [x] `ALLOW_UNSAFE_COMMANDS=false` unchanged

## Completion

Phase 4 completed on 2026-06-04:

- Hermes UI exposed at `https://hermes-ui.strategistudio.no`
- Cloudflare Access verified with unauthenticated `302` redirect
- Documentation and GSD state updated
- No backend code changed in this documentation commit

*Plan created: 2026-06-03*
*Plan completed: 2026-06-04*
