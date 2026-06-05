# Phase 7: Verification

**Status:** Pending — fill after execute (task 7.5)

## Local checks

```bash
.venv/bin/python -m pytest -q
grep -R "shell=True" backend/ || true
grep -R "hermes -z" backend/ || true
grep -R "tunnel list" backend/ || true
```

Expected:

- [ ] pytest passes
- [ ] No shell=True
- [ ] No tunnel list in backend
- [ ] GET /api/operations includes `cloudflare_tunnel`
- [ ] Write routes unchanged (POST restart, POST bob/tasks only)

## Bob checks

- [ ] Bob pulled feat commit
- [ ] `/api/operations` — `cloudflare_tunnel` with hostname, tunnel_name, cloudflared, edge_probe
- [ ] No secrets in JSON (no `.cloudflared` credential content, no tokens)
- [ ] Dashboard «Drift og tjenester» shows Cloudflare Tunnel + local observation disclaimer
- [ ] Edge probe status documented (expect 302 + Access redirect)

## Requirements

| ID | Status | Notes |
|----|--------|-------|
| OPS-01 | pending | |
| OPS-02 | pending | |
| OPS-03 | pending | |
| SEC-01 | pending | |
| SEC-02 | pending | |
