# Phase 6G: Bob Result Summary Fallback - Plan

```xml
<phase id="6G" name="Bob Result Summary Fallback">
  <goal>Unblock 6E UAT when Bob completes kanban tasks with latest_summary but null task.result.</goal>
  <constraints>
    <constraint>No new backend routes.</constraint>
    <constraint>No new write actions.</constraint>
    <constraint>No terminal/chat/shell UI.</constraint>
    <constraint>No Hermes Agent source edits.</constraint>
    <constraint>Keep existing POST /api/bob/tasks and read-only list/show routes.</constraint>
  </constraints>
  <task id="6G.1" name="Map completed task result shape">
    <work>Verify a completed Bob task can have result=null, latest_summary set, and optional metadata file output.</work>
  </task>
  <task id="6G.2" name="Surface latest_summary safely">
    <work>Use latest_summary as display/copy fallback in existing dashboard detail/result helpers.</work>
  </task>
  <task id="6G.3" name="Test deploy verify UAT">
    <work>Run local tests/security checks, deploy, and confirm completed Bob task details expose the summary.</work>
  </task>
</phase>
```
