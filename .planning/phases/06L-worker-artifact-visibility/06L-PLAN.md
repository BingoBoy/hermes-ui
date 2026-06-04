# Phase 6L: Worker Artifact Visibility - Plan

```xml
<phase id="6L" name="Worker Artifact Visibility">
  <goal>Show small, safe worker-generated artifacts in Bob task details without introducing arbitrary file access.</goal>
  <constraints>
    <constraint>Use existing GET /api/bob/tasks/{id}.</constraint>
    <constraint>No new backend routes.</constraint>
    <constraint>No new write actions.</constraint>
    <constraint>No client-supplied file paths.</constraint>
    <constraint>Only read artifact paths from kanban show metadata when they resolve under the task workspace.</constraint>
  </constraints>
  <task id="6L.1" name="Map worker artifact metadata">
    <work>Confirm artifact metadata appears as runs[].metadata.file_path and task.workspace_path in kanban show output.</work>
  </task>
  <task id="6L.2" name="Add safe read-only artifact exposure">
    <work>Read a bounded number of small text artifacts under the task workspace and include relative path, size, and content in task detail response.</work>
  </task>
  <task id="6L.3" name="Render and verify artifacts">
    <work>Render artifacts in task detail with copy action, add tests, deploy, and verify t_7b978d4f shows morgenbrief.md.</work>
  </task>
</phase>
```
