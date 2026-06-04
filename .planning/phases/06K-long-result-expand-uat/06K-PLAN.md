# Phase 6K: Long Result Expand UAT - Plan

```xml
<phase id="6K" name="Long Result Expand UAT">
  <goal>Close the remaining expand/collapse UAT gap for long Bob result text.</goal>
  <constraints>
    <constraint>No code changes unless UAT finds a defect.</constraint>
    <constraint>No new backend routes.</constraint>
    <constraint>No new write actions.</constraint>
    <constraint>No terminal/chat/shell UI.</constraint>
  </constraints>
  <task id="6K.1" name="Find or create long result candidate">
    <work>Prefer existing Bob data; fall back to local UI function smoke with synthetic long result text.</work>
  </task>
  <task id="6K.2" name="Verify expand/collapse behavior">
    <work>Confirm Inbox-style text uses preview, expands to full text, and collapses back; confirm detail PRE uses CSS collapse with full text preserved.</work>
  </task>
  <task id="6K.3" name="Document outcome">
    <work>Record pass/fail and whether a code fix is needed.</work>
  </task>
</phase>
```
