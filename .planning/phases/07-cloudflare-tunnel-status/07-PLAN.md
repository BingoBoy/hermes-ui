# Phase 7: Cloudflare Tunnel Status — Plan

**Created:** 2026-06-04  
**Status:** Ready for execute  
**Milestone:** v1.1 Operational Visibility  
**Requirements:** OPS-01, OPS-02, OPS-03, SEC-01, SEC-02

```xml
<phase id="7" name="Cloudflare Tunnel Status">
  <goal>Add read-only Cloudflare tunnel / cloudflared visibility by extending GET /api/operations and «Drift og tjenester».</goal>
  <depends_on>Phase 6 (operations API + dashboard), Phase 4 (tunnel hostname and Access flow documented)</depends_on>
  <constraints>
    <constraint>Read-only — no new POST/write routes.</constraint>
    <constraint>No shell=True; fixed argv only via _run_read_only from backend.status.</constraint>
    <constraint>No cloudflared tunnel list, cert.pem, ~/.cloudflared/*.json, or Cloudflare API tokens.</constraint>
    <constraint>Edge probe: HTTP status + Location host only; never store response body.</constraint>
    <constraint>UI disclaimer: local agent observed — not full Cloudflare edge health.</constraint>
    <constraint>Hostname, tunnel name, service target from server Settings/env only.</constraint>
    <constraint>launchctl for cloudflared only if Bob preflight documents a stable label.</constraint>
    <constraint>Preserve Bob-first dashboard order; tunnel block inside operations-section.</constraint>
  </constraints>

  <task id="7.0" name="Bob preflight — cloudflared observation">
    <work>
      SSH BobRemote (or local Bob) and run read-only checklist from 07-RESEARCH.md.
      Record in 07-PREFLIGHT.md: binary path, version, pgrep output, launchctl grep result,
      edge curl status line and Location host. Decide launchctl.included yes/no.
    </work>
    <verify>
      <check>cloudflared --version succeeds</check>
      <check>pgrep shows cloudflared process OR document why not</check>
      <check>Edge probe returns 302 (or document actual status)</check>
      <check>Confirm tunnel list still fails without cert — do not add to code</check>
    </verify>
    <output>.planning/phases/07-cloudflare-tunnel-status/07-PREFLIGHT.md</output>
    <gate>Do not implement launchctl subsection unless preflight finds repeatable label</gate>
  </task>

  <task id="7.1" name="Settings and env">
    <work>
      Add to backend/config.py Settings + get_settings():
      - hermes_public_hostname (HERMES_PUBLIC_HOSTNAME, default hermes-ui.strategistudio.no)
      - hermes_cloudflare_tunnel_name (HERMES_CLOUDFLARE_TUNNEL_NAME, default bob-mac-mini-m4)
      - hermes_ops_edge_probe (HERMES_OPS_EDGE_PROBE, default true)
      - hermes_cloudflared_bin (HERMES_CLOUDFLARED_BIN, default /opt/homebrew/bin/cloudflared) optional if which is enough
      - hermes_cloudflared_launchd_label (HERMES_CLOUDFLARED_LAUNCHD_LABEL, default empty) set only if 7.0 finds label
      Document in .env.example and docs/architecture/deployment.md § Cloudflare (non-secret defaults).
    </work>
    <files>backend/config.py, .env.example, docs/architecture/deployment.md</files>
    <verify>
      <check>get_settings() picks up env overrides in unit test</check>
      <check>No secret env vars added</check>
    </verify>
  </task>

  <task id="7.2" name="Backend cloudflare_tunnel status">
    <work>
      In backend/operations.py:
      - Import _run_read_only from backend.status (avoid duplicating subprocess helper).
      - Implement _cloudflared_binary_status(settings) using which or fixed bin path + cloudflared --version.
      - Implement _cloudflared_process_status() using pgrep -lf cloudflared (fixed argv).
      - Implement _edge_probe_status(settings) when hermes_ops_edge_probe: curl -D - -o /dev/null to
        https://{hostname}/api/status; parse status code and location host; set access_redirect boolean.
      - Optional _cloudflared_launchctl_status(settings) if label configured from 7.0.
      - Implement _cloudflare_tunnel_status(settings) assembling observation_scope, disclaimer,
        public_hostname, tunnel_name, service_target (http://127.0.0.1:{port}), cloudflared, edge_probe, launchctl.
      - Add cloudflare_tunnel key to get_operations_status() return dict.
      Fail closed: errors as structured strings; never read credential files.
    </work>
    <files>backend/operations.py</files>
    <verify>
      <check>get_operations_status includes cloudflare_tunnel with required keys</check>
      <check>grep shell=True backend/ — no matches</check>
      <check>grep cloudflared tunnel backend/ — no matches</check>
    </verify>
  </task>

  <task id="7.3" name="Dashboard Cloudflare Tunnel block">
    <work>
      In backend/dashboard.py operations-section HTML:
      - Add div#operations-tunnel-wrap after operations-agents-wrap, before docker wrap.
      - Add short disclaimer paragraph matching observation_scope.
      In renderOperations():
      - Render tunnel card from data.cloudflare_tunnel: hostname, tunnel name, cloudflared badges,
        edge probe status, access redirect ja/nei.
      - Use escapeHtml; no raw stderr in UI.
      - Update served HTML test strings if present in tests/test_api.py.
    </work>
    <files>backend/dashboard.py, tests/test_api.py (HTML assertions only if existing pattern)</files>
    <verify>
      <check>Dashboard HTML contains Cloudflare Tunnel and disclaimer text</check>
      <check>renderOperations still handles missing cloudflare_tunnel gracefully</check>
    </verify>
  </task>

  <task id="7.4" name="Tests">
    <work>
      Extend tests/test_operations.py:
      - test_operations_includes_cloudflare_tunnel
      - test_cloudflare_tunnel_mocks_version_pgrep_curl (monkeypatch _run_read_only or helpers)
      - test_edge_probe_302_sets_access_redirect
      - test_edge_probe_disabled_when_flag_false
      - test_no_secrets_in_tunnel_payload (no .cloudflared paths in JSON string for mocked cred-like output)
      Update tests/test_api.py if needed:
      - test_only_allowlisted_write_route_exists unchanged
      - operations endpoint still 200
      Run: .venv/bin/python -m pytest -q
    </work>
    <files>tests/test_operations.py, tests/test_api.py</files>
    <verify>
      <check>pytest all green</check>
      <check>grep hermes -z backend/ — no matches</check>
    </verify>
  </task>

  <task id="7.5" name="Bob deploy and verify">
    <work>
      git push origin main; Bob git pull --ff-only; restart Hermes UI LaunchAgent if Python changed:
      launchctl kickstart -k gui/$(id -u)/no.truls.hermes-ui
      Verify loopback:
      curl -s http://127.0.0.1:8787/api/operations | python3 -m json.tool
      Confirm cloudflare_tunnel present; no env values or credential paths in output.
      Confirm dashboard shows Cloudflare Tunnel under Drift og tjenester.
      Write 07-VERIFICATION.md with Bob evidence.
    </work>
    <output>.planning/phases/07-cloudflare-tunnel-status/07-VERIFICATION.md</output>
    <verify>
      <check>/api/operations on Bob includes cloudflare_tunnel</check>
      <check>edge_probe.http_status matches preflight (expect 302)</check>
      <check>No secrets in JSON or dashboard HTML source</check>
    </verify>
  </task>
</phase>
```

## Goal-backward checklist

| Requirement | Task | Evidence |
|-------------|------|----------|
| OPS-01 Tunnel status in UI | 7.2–7.3, 7.5 | API + dashboard + Bob |
| OPS-02 Allowlisted read-only checks | 7.2 | _run_read_only, fixed argv |
| OPS-03 No secrets in output | 7.2, 7.4, 7.5 | tests + manual JSON review |
| SEC-01 No new POST routes | 7.4 | test_api allowlist |
| SEC-02 No shell=True | 7.2, 7.4 | grep |

## Verification commands

```bash
.venv/bin/python -m pytest -q
grep -R "shell=True" backend/ || true
grep -R "hermes -z" backend/ || true
grep -R "tunnel list" backend/ || true
curl -s http://127.0.0.1:8787/api/operations | python3 -m json.tool
```

## Bob deploy

```bash
cd /Users/trulsdahl/Dev/hermes-ui
git pull --ff-only origin main
launchctl kickstart -k gui/$(id -u)/no.truls.hermes-ui
curl -s http://127.0.0.1:8787/api/operations | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('cloudflare_tunnel',{}).keys())"
```

## Out of scope

- Gateway start/stop (5B)
- `cloudflared tunnel list` / tunnel info CLI
- Cloudflare Dashboard API
- LM Studio / n8n / Docker tunnel routes
- Bob worker `hermes-assignee`
- New POST routes or tunnel start/stop/restart controls

## Execute order

```text
7.0 (Bob preflight) → 7.1 → 7.2 → 7.3 → 7.4 → 7.5
```

7.0 may run on Bob before MacBook code if SSH available; record results before coding launchctl optional block.

## Next after execute

`/gsd-execute-phase 7` or `/gsd-verify-work 7` after implementation.
