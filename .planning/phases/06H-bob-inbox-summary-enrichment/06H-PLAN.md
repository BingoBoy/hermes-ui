# Phase 6H: Bob Inbox Summary Enrichment - Plan

```xml
<phase id="6H" name="Bob Inbox Summary Enrichment">
  <goal>Make Bob Inbox result actions work from the task list when completed tasks only expose latest_summary through kanban show.</goal>
  <constraints>
    <constraint>No new backend routes.</constraint>
    <constraint>No new write actions.</constraint>
    <constraint>No terminal/chat/shell UI.</constraint>
    <constraint>No Hermes Agent source edits.</constraint>
    <constraint>Use existing GET /api/bob/tasks and GET /api/bob/tasks/{id} behavior.</constraint>
  </constraints>
  <task id="6H.1" name="Confirm list/detail gap">
    <work>Verify Bob list output lacks latest_summary while show output includes it.</work>
  </task>
  <task id="6H.2" name="Enrich read-only list response">
    <work>For a bounded number of done/completed/failed/blocked tasks with empty result, call fixed kanban show and copy latest_summary into the list task object.</work>
  </task>
  <task id="6H.3" name="Test deploy verify Inbox">
    <work>Run tests/security checks, deploy, and confirm t_7b978d4f has latest_summary in GET /api/bob/tasks.</work>
  </task>
</phase>
```
