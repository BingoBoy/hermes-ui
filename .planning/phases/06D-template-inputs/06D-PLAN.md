# Phase 6D — Template Inputs — PLAN

<phase id="6D" name="Template Inputs">
  <goal>
    Add safe optional input fields to Bob task templates while continuing to use the existing POST /api/bob/tasks endpoint.
  </goal>

  <constraints>
    <constraint>No terminal UI</constraint>
    <constraint>No chat UI</constraint>
    <constraint>No hermes -z</constraint>
    <constraint>No shell=True</constraint>
    <constraint>No client-controlled CLI flags</constraint>
    <constraint>No new unsafe write-actions</constraint>
    <constraint>Use existing POST /api/bob/tasks</constraint>
    <constraint>No new backend routes unless strictly necessary</constraint>
    <constraint>Inputs must only become plain text inside the Bob task body</constraint>
  </constraints>

  <tasks>
    <task id="6D.1" name="Map existing template flow">
      <description>
        Locate the existing 6C task template implementation and identify the smallest safe integration point for optional template inputs.
      </description>
      <context>
        backend/dashboard.py, tests/test_api.py, docs/api/bob-interaction.md, docs/security/README.md, README.md
      </context>
      <verification>
        Confirm current templates use submitBobTaskPayload and POST /api/bob/tasks without new backend routes.
      </verification>
      <commit>
        No commit required unless planning docs are added.
      </commit>
    </task>

    <task id="6D.2" name="Add optional template inputs">
      <description>
        Add optional, controlled input fields for relevant Bob task templates and safely compose the task payload before sending it through the existing task submission flow.
      </description>
      <verification>
        Confirm each template still sends through POST /api/bob/tasks, manual task creation still works, and ALLOW_BOB_TASKS=false still hides the template UI.
      </verification>
      <commit>
        git commit -m "feat(6D): add inputs for Bob task templates"
      </commit>
    </task>

    <task id="6D.3" name="Document and test template inputs">
      <description>
        Add or update tests and documentation for template inputs, including safety boundaries and expected UI behavior.
      </description>
      <verification>
        Tests pass, documentation states that inputs only affect task text and do not add new backend routes, shell access, terminal UI or CLI flags.
      </verification>
      <commit>
        git commit -m "docs(6D): document Bob template inputs"
      </commit>
    </task>
  </tasks>
</phase>

## Wave 1

Execute 6D.2 then 6D.3 (docs/tests can ship with implementation in one commit split per plan).
