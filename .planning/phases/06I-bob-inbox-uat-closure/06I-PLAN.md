# Phase 6I: Bob Inbox UAT Closure - Plan

```xml
<phase id="6I" name="Bob Inbox UAT Closure">
  <goal>Close the Bob Inbox result-action UAT after 6F/6G/6H unblocked assignment, summary fallback, and list enrichment.</goal>
  <constraints>
    <constraint>No code changes unless UAT finds a defect.</constraint>
    <constraint>No new backend routes.</constraint>
    <constraint>No new write actions.</constraint>
    <constraint>No terminal/chat/shell UI.</constraint>
  </constraints>
  <task id="6I.1" name="Set up UAT path to Bob UI">
    <work>Use an SSH local tunnel to Bob's existing loopback-bound Hermes UI, avoiding Cloudflare Access during automated UAT.</work>
  </task>
  <task id="6I.2" name="Verify Bob Inbox result actions">
    <work>Confirm Bob Inbox shows completed task summary, result actions, and detail fallback for t_7b978d4f.</work>
  </task>
  <task id="6I.3" name="Document UAT outcome">
    <work>Record pass/fail results, limitations, and whether 6E UAT can close.</work>
  </task>
</phase>
```
