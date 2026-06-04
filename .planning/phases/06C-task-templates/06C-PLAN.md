# Phase 6C Plan: Task Templates

**Goal:** Add safe one-click Bob task templates to Hermes UI using existing `POST /api/bob/tasks`.

**Depends on:** 5C (task create), 5D (list/detail), 6A–6B (post-create UX)

**Status:** Complete — verified 2026-06-04 (UAT 7/7 pass, 1 skipped)

**Context:** `.planning/phases/06C-task-templates/06C-CONTEXT.md`

---

## Preconditions

- `ALLOW_BOB_TASKS=true` on target server (Bob already configured per project state).
- No Bob CLI re-verify required — no argv or route changes.
- Baseline commit: `14905ce` or later on `main`.

---

## Executable plan (XML)

```xml
<phase id="6C" name="Task Templates">
  <goal>
    Add safe one-click Bob task templates to Hermes UI using the existing POST /api/bob/tasks endpoint.
    No new backend routes unless discovery during 6C.1 proves POST cannot be reused (expected: unchanged).
  </goal>

  <depends_on>
    <phase id="5C">POST /api/bob/tasks, bob_tasks.py allowlist</phase>
    <phase id="5D">GET task list/detail</phase>
    <phase id="6A-6B">loadBobHistory, scheduleBobHighlight, loadBobTaskDetail after create</phase>
  </depends_on>

  <constraints>
    <constraint>No terminal UI</constraint>
    <constraint>No chat UI</constraint>
    <constraint>No hermes -z</constraint>
    <constraint>No shell=True</constraint>
    <constraint>No client-controlled CLI flags</constraint>
    <constraint>No new unsafe write-actions</constraint>
    <constraint>No gateway start/stop</constraint>
    <constraint>Backend bind remains 127.0.0.1 only</constraint>
    <constraint>Use existing POST /api/bob/tasks with { title, body } only</constraint>
    <constraint>No new backend routes unless strictly necessary</constraint>
    <constraint>Templates hardcoded in frontend — no server template registry</constraint>
  </constraints>

  <tasks>
    <task id="6C.1" name="Refactor shared Bob task submit helper">
      <description>
        In backend/dashboard.py, extract submitBobTaskPayload({ title, body }) from submitBobTask so manual form and templates share one POST /api/bob/tasks path, result handling, list refresh, and detail open. Do not change backend Python modules unless POST contract inspection fails.
      </description>
      <files>
        <file>backend/dashboard.py</file>
        <file>backend/main.py</file>
        <file>backend/bob_tasks.py</file>
        <file>docs/api/bob-interaction.md</file>
      </files>
      <steps>
        <step>Read submitBobTask (~1016–1055) and fetchJson error handling.</step>
        <step>Confirm API payload: JSON.stringify({ title, body }) — same as manual form.</step>
        <step>Extract async submitBobTaskPayload({ title, body }) returning success/failure; keep setBobTaskResult, clearBobTaskResult, scheduleBobHighlight, loadBobHistory, loadBobTaskDetail on success.</step>
        <step>Wire bob-task-form submit to call helper with input values (behavior unchanged).</step>
      </steps>
      <verification>
        <check>Manual form still calls POST /api/bob/tasks with title + body only</check>
        <check>rg 'shell=True' backend/ — no matches</check>
        <check>rg '@app\.(post|put|patch|delete)' backend/main.py — only existing write routes (bob/tasks, hermes/restart)</check>
        <check>.venv/bin/python -m pytest tests/test_api.py::test_dashboard_includes_bob_task_submission_ui -q</check>
      </verification>
      <commit>refactor(6C): extract shared Bob task submit helper</commit>
    </task>

    <task id="6C.2" name="Add Bob task template UI">
      <description>
        Add «Bob task-maler» sub-section inside #bob-task-section above #bob-task-form: five one-click buttons, hardcoded BOB_TASK_TEMPLATES constant, compact CSS grid, Norwegian labels, disable all template buttons + manual submit during in-flight POST.
      </description>
      <files>
        <file>backend/dashboard.py</file>
        <file>tests/test_api.py</file>
      </files>
      <templates>
        <template ui_label="Morgenbrief" title="Lag morgenbrief">
          <body>Lag en kort morgenbrief for Truls med prioriteringer, relevante oppgaver og anbefalt fokus for arbeidsdagen.</body>
        </template>
        <template ui_label="Ukesrapport" title="Lag ukesrapport">
          <body>Lag en ukesrapport for Truls med oppsummering av viktig arbeid, åpne punkter, risikoer og anbefalte neste steg.</body>
        </template>
        <template ui_label="Konkurrentanalyse" title="Kjør konkurrentanalyse">
          <body>Kjør en konkurrentanalyse for Tirna med fokus på relevante fagskole- og kursaktører, tydelige funn, kilder og anbefalte tiltak.</body>
        </template>
        <template ui_label="Nettsideanalyse" title="Analyser nettside">
          <body>Analyser en nettside for Tirna med fokus på budskap, konvertering, SEO, brukerreise og konkrete forbedringsforslag. Be om URL dersom den ikke er oppgitt i oppgaven.</body>
        </template>
        <template ui_label="Markedsføringsstatus" title="Lag status for markedsføring">
          <body>Lag en kort status for markedsføring med pågående aktiviteter, flaskehalser, prioriterte tiltak og forslag til hva Truls bør følge opp først.</body>
        </template>
      </templates>
      <html_requirements>
        <item>Section id bob-task-templates, h3 «Bob task-maler», intro copy (one-click async kanban)</item>
        <item>Container #bob-template-buttons with type=button controls (no nested form)</item>
        <item>Hidden when ALLOW_BOB_TASKS=false — same gate as #bob-task-form via updateBobTasksUi</item>
      </html_requirements>
      <js_requirements>
        <item>const BOB_TASK_TEMPLATES = [ { id, label, title, body }, ... ]</item>
        <item>sendBobTaskTemplate(template) → submitBobTaskPayload({ title, body })</item>
        <item>Loading: button text «Sender …»; success: «Oppgave sendt til Bob» + task_id/audit_id; error: «Kunne ikke sende oppgave»</item>
      </js_requirements>
      <css_requirements>
        <item>.bob-template-grid — flex/grid wrap, gap consistent with .bob-section</item>
        <item>.bob-template-btn — match existing button/card tone</item>
      </css_requirements>
      <test_requirements>
        <item>Add test_dashboard_includes_bob_task_templates_ui asserting: bob-task-templates, Bob task-maler, BOB_TASK_TEMPLATES, Morgenbrief, submitBobTaskPayload</item>
      </test_requirements>
      <verification>
        <check>pytest tests/test_api.py -q</check>
        <check>rg 'hermes -z|chat -q|shell=True' backend/dashboard.py — no matches</check>
        <check>rg 'bob-template|BOB_TASK_TEMPLATES|submitBobTaskPayload' backend/dashboard.py</check>
        <check>Manual (ALLOW_BOB_TASKS=true): click Morgenbrief → 202 → task in Bob-oppgaver list → manual form still works</check>
      </verification>
      <commit>feat(6C): add Bob task templates to dashboard</commit>
    </task>

    <task id="6C.3" name="Document task templates">
      <description>
        Document frontend-only templates, five preset names, same POST flow, unchanged security boundaries.
      </description>
      <files>
        <file>docs/api/bob-interaction.md</file>
        <file>docs/security/README.md</file>
        <file>README.md</file>
      </files>
      <doc_requirements>
        <item>docs/api/bob-interaction.md — new UI subsection «Bob task-maler (6C)» under UI</item>
        <item>docs/security/README.md — note templates send only allowlisted title/body via existing endpoint</item>
        <item>README.md — mention Bob task-maler in dashboard features when ALLOW_BOB_TASKS=true</item>
      </doc_requirements>
      <verification>
        <check>Docs state: no new routes, no terminal/chat/shell, hardcoded frontend prompts</check>
        <check>Sub-phases table in bob-interaction.md includes 6C row</check>
      </verification>
      <commit>docs(6C): document Bob task templates</commit>
    </task>
  </tasks>

  <phase_verification>
    <command>.venv/bin/python -m pytest -q</command>
    <command>rg 'shell=True' backend/</command>
    <command>rg 'hermes -z' backend/</command>
    <command>python -c "from backend.main import app; writes=[r for r in app.routes if hasattr(r,'methods') and r.methods & {'POST','PUT','PATCH','DELETE'}]; assert len(writes)==2"</command>
    <manual>Start uvicorn locally; send one template; confirm list refresh; confirm manual create; confirm templates hidden when gate off</manual>
  </phase_verification>

  <deploy>
    <macbook>
      <step>git push origin main</step>
    </macbook>
    <bob>
      <step>ssh BobRemote</step>
      <step>cd /Users/trulsdahl/Dev/hermes-ui &amp;&amp; git pull --ff-only origin main</step>
      <step>source .venv/bin/activate &amp;&amp; pip install -r requirements.txt  # if needed</step>
      <step>launchctl kickstart -k gui/$(id -u)/no.truls.hermes-ui</step>
      <step>curl -s http://127.0.0.1:8787/api/status | head</step>
    </bob>
    <external>https://hermes-ui.strategistudio.no — Bob task-maler visible; one template send works</external>
  </deploy>

  <success_criteria>
    <criterion>Five templates visible in «Bob task-maler» when ALLOW_BOB_TASKS=true</criterion>
    <criterion>One click creates task via POST /api/bob/tasks; task appears in Bob-oppgaver after refresh</criterion>
    <criterion>Manual «Send oppgave til Bob» unchanged</criterion>
    <criterion>No new backend routes; no shell=True; no client CLI flags</criterion>
    <criterion>Documentation updated</criterion>
  </success_criteria>

  <out_of_scope>
    <item>User-editable or server-stored templates</item>
    <item>URL picker modal for nettsideanalyse</item>
    <item>Gateway start/stop, terminal, chat, hermes -z</item>
    <item>New service actions or LaunchAgent changes for hermes-ui</item>
    <item>Dashboard redesign beyond compact template grid</item>
  </out_of_scope>
</phase>
```

---

## Task summary (human)

| ID | Name | Commit |
|----|------|--------|
| 6C.1 | Refactor shared submit helper | `refactor(6C): extract shared Bob task submit helper` |
| 6C.2 | Template UI + tests | `feat(6C): add Bob task templates to dashboard` |
| 6C.3 | Documentation | `docs(6C): document Bob task templates` |

**Wave:** 6C.1 → 6C.2 → 6C.3 (sequential; 6C.2 depends on helper from 6C.1).

---

## Integration map

```text
#bob-task-section
  ├── h2 Send oppgave til Bob
  ├── #bob-task-templates (NEW)
  │     └── buttons → submitBobTaskPayload({ title, body })
  ├── #bob-task-form (unchanged)
  │     └── submit → submitBobTaskPayload(inputs)
  └── #bob-task-result (shared feedback)

POST /api/bob/tasks  →  backend/bob_tasks.py (unchanged)
GET  /api/bob/tasks  →  loadBobHistory (unchanged)
```

---

## Next command

```text
/gsd-execute-phase 6C
```
