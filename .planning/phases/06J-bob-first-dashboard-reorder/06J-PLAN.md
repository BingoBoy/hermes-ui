# Phase 6J: Bob-First Dashboard Reorder - Plan

```xml
<phase id="6J" name="Bob-First Dashboard Reorder">
  <goal>Put communication with Bob at the top of the dashboard, ahead of operational status and logs.</goal>
  <constraints>
    <constraint>Frontend-only in backend/dashboard.py.</constraint>
    <constraint>No new backend routes.</constraint>
    <constraint>No new write actions.</constraint>
    <constraint>No terminal/chat/shell UI.</constraint>
    <constraint>No changes to POST /api/bob/tasks.</constraint>
  </constraints>
  <task id="6J.1" name="Map current dashboard section order">
    <work>Confirm current order is status/logs before Bob communication sections.</work>
  </task>
  <task id="6J.2" name="Reorder Bob communication sections first">
    <work>Move Bob Inbox, Send oppgave til Bob, and Bob-oppgaver before operational status cards and gateway logs.</work>
  </task>
  <task id="6J.3" name="Test browser-smoke deploy">
    <work>Add section-order test, run verification, browser-smoke, deploy to Bob, and verify first viewport prioritizes Bob communication.</work>
  </task>
</phase>
```
