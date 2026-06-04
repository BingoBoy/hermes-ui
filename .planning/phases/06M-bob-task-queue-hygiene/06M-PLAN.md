# Phase 6M: Bob Task Queue Hygiene - Plan

```xml
<phase id="6M" name="Bob Task Queue Hygiene">
  <goal>Make old unassigned and blocked Bob tasks easier to understand without mutating the kanban board.</goal>
  <constraints>
    <constraint>Read-only UI only.</constraint>
    <constraint>No delete/archive/cleanup write action.</constraint>
    <constraint>No new backend routes.</constraint>
    <constraint>No terminal/chat/shell UI.</constraint>
  </constraints>
  <task id="6M.1" name="Map queue clutter signals">
    <work>Use existing task list fields: status and assignee.</work>
  </task>
  <task id="6M.2" name="Add read-only assignee labels">
    <work>Add Assignee column and mark ready tasks without assignee as Legacy unassigned.</work>
  </task>
  <task id="6M.3" name="Test deploy verify queue hygiene">
    <work>Add tests, run verification, deploy, and confirm Bob HTML serves the labels.</work>
  </task>
</phase>
```
