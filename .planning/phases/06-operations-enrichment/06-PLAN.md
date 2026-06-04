# Phase 6: Operations Enrichment — Plan

**Created:** 2026-06-04  
**Status:** Planned  
**Requirements:** OPS-02, OPS-03

```xml
<phase id="6" name="Operations Enrichment">
  <goal>Add read-only LaunchAgent and optional Docker operational views for Bob daily operations.</goal>
  <depends_on>Phases 1–5 (read-only API, logs, service actions), v2.1-bob-ux layout</depends_on>
  <constraints>
    <constraint>Read-only — no new POST/write routes.</constraint>
    <constraint>No shell=True; fixed argv only; no client-supplied paths or labels.</constraint>
    <constraint>Do not expose plist EnvironmentVariables values or Cloudflare credentials.</constraint>
    <constraint>Preserve Bob-first dashboard order (Inbox → Tasks → History → Ops → Statuskort → Logs).</constraint>
    <constraint>Bind remains 127.0.0.1:8787.</constraint>
  </constraints>

  <task id="6.1" name="Verify operational sources on Bob">
    <work>SSH BobRemote read-only checklist from 06-RESEARCH.md.</work>
    <verify>
      <check>launchctl print succeeds for no.truls.hermes-ui and ai.hermes.gateway</check>
      <check>Both plists readable; paths match deployment.md</check>
      <check>Document docker relevance (on/off for HERMES_OPS_INCLUDE_DOCKER)</check>
    </verify>
    <output>06-VERIFICATION.md § Bob preflight (or 06-DISCUSSION-LOG.md notes)</output>
  </task>

  <task id="6.2" name="Backend operations provider">
    <work>
      Add backend/operations.py and Settings fields for allowlisted labels/paths
      (HERMES_UI_LAUNCHD_LABEL, HERMES_UI_PLIST_PATH, HERMES_GATEWAY_PLIST_PATH,
      HERMES_OPS_INCLUDE_DOCKER). Implement get_operations_status(settings):
      plistlib metadata (no env values), _launchctl_status per label,
      optional launchctl print with fixed domain path, optional docker block when gated.
    </work>
    <files>backend/operations.py, backend/config.py</files>
    <verify>
      <check>Unit tests with mocked plist/subprocess</check>
      <check>grep shell=True backend/ — no matches</check>
    </verify>
  </task>

  <task id="6.3" name="GET /api/operations">
    <work>Register GET /api/operations in backend/main.py returning get_operations_status JSON.</work>
    <files>backend/main.py</files>
    <verify>
      <check>tests/test_api.py: endpoint returns 200 and launch_agents array</check>
      <check>test_only_allowlisted_write_route_exists still passes (only GET added)</check>
    </verify>
  </task>

  <task id="6.4" name="Dashboard «Drift og tjenester»">
    <work>
      In backend/dashboard.py: fetch /api/operations on refresh; render cards for each
      launch agent (label, plist path, program summary, log paths, running badge);
      docker subsection only when included=true. Place section after bob-history, before status grid.
    </work>
    <files>backend/dashboard.py, tests/test_api.py</files>
    <verify>
      <check>test_dashboard_orders_bob_communication_before_operations updated for ops section</check>
      <check>HTML contains Drift og tjenester and launch agent labels</check>
    </verify>
  </task>

  <task id="6.5" name="Docs and security regression">
    <work>
      Update docs/architecture/deployment.md (operations API pointer),
      docs/security/README.md (read-only ops boundary). Run full pytest and security greps.
    </work>
    <files>docs/architecture/deployment.md, docs/security/README.md</files>
  </task>

  <task id="6.6" name="Deploy and verify on Bob">
    <work>
      git pull on Bob; restart no.truls.hermes-ui LaunchAgent if needed;
      curl /api/operations; confirm dashboard section on loopback or tunnel UAT.
    </work>
    <output>06-VERIFICATION.md</output>
  </task>
</phase>
```

## Goal-backward checklist

| Criterion | Task | Evidence |
|-----------|------|----------|
| OPS-02 LaunchAgent details with verified label/plist | 6.1–6.4 | API + dashboard + Bob verify |
| OPS-03 Docker only if relevant | 6.1, 6.2 | Bob assess + config gate |
| Operational cards read-only | 6.2–6.4 | No new POST routes; tests |
| Security boundaries preserved | 6.2, 6.5 | greps + allowlist test |
| Bob UX layout preserved | 6.4 | ordering test |

## Verification commands

```bash
.venv/bin/python -m pytest -q
grep -R "shell=True" backend/ || true
grep -R "hermes -z" backend/ || true
curl -s http://127.0.0.1:8787/api/operations | python3 -m json.tool
```

## Bob deploy

```bash
cd /Users/trulsdahl/Dev/hermes-ui
git pull --ff-only origin main
launchctl kickstart -k gui/$(id -u)/no.truls.hermes-ui
curl -s http://127.0.0.1:8787/api/operations | head
```

## Out of scope

- Phase 5B start/stop
- Cloudflare tunnel live status card (OPS-01)
- Hermes UI log viewer for `~/.hermes-ui/logs/*`
- LM Studio / n8n service cards

## Next after execute

`/gsd-execute-phase 6` (or execute plans 6.1–6.6 sequentially)
