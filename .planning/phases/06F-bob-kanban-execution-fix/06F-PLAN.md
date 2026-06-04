# Phase 6F: Bob Kanban Execution Fix - Plan

```xml
<phase id="6F" name="Bob Kanban Execution Fix">
  <goal>Ensure Bob tasks created by Hermes UI are assigned to a spawnable server-controlled Hermes profile, then separate UI task creation from any Hermes Agent worker protocol failures.</goal>
  <constraints>
    <constraint>Use existing POST /api/bob/tasks.</constraint>
    <constraint>No client-controlled assignee or CLI flags.</constraint>
    <constraint>No terminal/chat/shell UI.</constraint>
    <constraint>No hermes -z.</constraint>
    <constraint>No shell=True.</constraint>
    <constraint>No gateway start/stop controls.</constraint>
  </constraints>
  <task id="6F.1" name="Map task creation + config">
    <work>Confirm current POST payload, fixed kanban argv, status/config patterns, tests, docs, and LaunchAgent env documentation.</work>
  </task>
  <task id="6F.2" name="Add server-controlled assignee for Bob tasks">
    <work>Add HERMES_BOB_TASK_ASSIGNEE, validate it as a simple profile string, and append --assignee only when configured server-side.</work>
  </task>
  <task id="6F.3" name="Document/test/deploy/verify execution behavior">
    <work>Update tests/docs, deploy to Bob, verify new tasks are not skipped_unassigned, and record any remaining protocol_violation as a Hermes Agent kanban-worker issue.</work>
  </task>
</phase>
```
