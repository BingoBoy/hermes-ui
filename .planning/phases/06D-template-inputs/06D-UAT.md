---
status: complete
phase: 06D-template-inputs
source: 06D-PLAN.md, 06D-IMPLEMENTATION-LOG.md
started: 2026-06-04T10:15:00Z
updated: 2026-06-04T12:30:00Z
---

## Current Test

[testing complete]

## Tests

### 1. Automated test suite
expected: pytest passes; no shell=True or hermes -z; exactly 2 write routes
result: pass
notes: 63 passed; write routes /api/hermes/restart, /api/bob/tasks

### 2. Bob deploy (5355872+)
expected: Bob serves dashboard with template inputs and buildBobTaskTemplatePayload
result: pass
notes: git at d2abf42; kickstart 2026-06-04; /api/status allow_bob_tasks true

### 3. Dashboard HTML includes template inputs
expected: Bob task-maler, per-template inputs, Send mal til Bob, buildBobTaskTemplatePayload
result: pass
notes: curl 127.0.0.1:8787/ on Bob

### 4. External dashboard (Cloudflare Access)
expected: |
  https://hermes-ui.strategistudio.no after Access login:
  Bob task-maler visible; inputs on relevant templates;
  Morgenbrief with/without focus; Nettsideanalyse with URL;
  Konkurrentanalyse with tema; tasks in Bob-oppgaver;
  manual form, Bob Inbox, gateway logs, Restart Gateway unchanged;
  no terminal/chat/gateway start/stop.
result: pass
reported: |
  User UAT 2026-06-04 — all 12 checklist items confirmed on production URL.

### 5. Templates gated when Bob tasks disabled
expected: ALLOW_BOB_TASKS=false hides template section (same as 5C/6C)
result: skipped
reason: Production Bob has ALLOW_BOB_TASKS=true; covered by unit tests and updateBobTasksUi

## Summary

total: 5
passed: 4
issues: 0
pending: 0
skipped: 1
blocked: 0

## Gaps

[none]
