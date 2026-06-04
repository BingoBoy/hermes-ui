# Phase 6E — PLAN

<phase id="6E" name="Task Result Actions">
  <goal>
    Add safe browser-only actions for Bob task results, focused on copying and reading results without introducing new backend write-actions.
  </goal>
  <constraints>
    <constraint>No terminal UI</constraint>
    <constraint>No chat UI</constraint>
    <constraint>No hermes -z</constraint>
    <constraint>No shell=True</constraint>
    <constraint>No client-controlled CLI flags</constraint>
    <constraint>No new unsafe write-actions</constraint>
    <constraint>Clipboard/copy actions must be browser-only</constraint>
  </constraints>
  <tasks>
    <task id="6E.1" name="Map existing result UI">…</task>
    <task id="6E.2" name="Add browser-only result actions">commit: feat(6E): add safe Bob result actions</task>
    <task id="6E.3" name="Document and test result actions">commit: docs(6E): document Bob result actions</task>
  </tasks>
</phase>
