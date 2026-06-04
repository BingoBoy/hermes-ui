# Phase 6C: Task Templates - Context

**Gathered:** 2026-06-04
**Status:** Ready for planning

<domain>

## Phase Boundary

Add safe one-click Bob task templates to the Hermes UI dashboard. Templates send predefined `title` + `body` through the existing `POST /api/bob/tasks` flow (5C). No new backend routes, no new CLI argv, no terminal/chat/shell, no client-controlled flags.

</domain>

<decisions>

## Implementation Decisions

### API and security
- **D-01:** No backend changes unless discovery proves POST cannot be reused (expected: unchanged).
- **D-02:** Templates are a hardcoded frontend constant only (`title` + `body` per template). No server-side template registry, no user-defined templates, no query params or extra JSON fields.
- **D-03:** Each template maps to API payload `{ title, body }` exactly like the manual form; backend validation limits unchanged (title 200, body 4000, no newlines in title).
- **D-04:** Reuse existing gates: section hidden/disabled when `ALLOW_BOB_TASKS=false` (same as manual form and Bob history).

### UX and placement
- **D-05:** Place templates inside the existing `#bob-task-section` card, **above** the manual form, as a sub-section **«Bob task-maler»** with short intro copy (one-click, async kanban — same framing as 5C).
- **D-06:** **One-click send** — clicking a template button POSTs immediately; no separate confirmation modal (Truls specified «ett klikk»).
- **D-07:** Manual form **«Send oppgave til Bob»** remains below templates; behavior unchanged.
- **D-08:** On success: reuse 6A–6B post-create flow — `setBobTaskResult` with `task_id` / `audit_id`, `scheduleBobHighlight`, `loadBobHistory()`, `loadBobTaskDetail(task_id)`.
- **D-09:** Loading/error copy in Norwegian: per-button «Sender …», success «Oppgave sendt til Bob», failure «Kunne ikke sende oppgave» (plus API detail when safe).
- **D-10:** While a template POST is in flight: disable all template buttons and manual submit to prevent double-submit; re-enable on completion (match manual form pattern).

### Template catalog (locked)
| UI label | `title` (API) | `body` (API) |
|----------|---------------|--------------|
| Morgenbrief | Lag morgenbrief | Lag en kort morgenbrief for Truls med prioriteringer, relevante oppgaver og anbefalt fokus for arbeidsdagen. |
| Ukesrapport | Lag ukesrapport | Lag en ukesrapport for Truls med oppsummering av viktig arbeid, åpne punkter, risikoer og anbefalte neste steg. |
| Konkurrentanalyse | Kjør konkurrentanalyse | Kjør en konkurrentanalyse for Tirna med fokus på relevante fagskole- og kursaktører, tydelige funn, kilder og anbefalte tiltak. |
| Nettsideanalyse | Analyser nettside | Analyser en nettside for Tirna med fokus på budskap, konvertering, SEO, brukerreise og konkrete forbedringsforslag. Be om URL dersom den ikke er oppgitt i oppgaven. |
| Markedsføringsstatus | Lag status for markedsføring | Lag en kort status for markedsføring med pågående aktiviteter, flaskehalser, prioriterte tiltak og forslag til hva Truls bør følge opp først. |

### Code structure
- **D-11:** Refactor minimal shared helper `submitBobTaskPayload({ title, body })` (or equivalent) used by both form submit and template buttons — avoid duplicating `fetchJson` POST logic.
- **D-12:** Implement in `backend/dashboard.py` only (embedded HTML/CSS/JS); extend `.bob-section` styles with a compact template button grid consistent with existing dashboard cards.
- **D-13:** Extend `tests/test_api.py` dashboard HTML assertions for template section labels when Bob tasks UI is present.

### Documentation
- **D-14:** Update `docs/api/bob-interaction.md` UI section, `docs/security/README.md` Bob Task Entry note, and `README.md` dashboard feature list.

### Claude's Discretion
- Exact CSS class names and grid layout (2-column vs wrap) as long as visual weight matches existing Bob sections.
- Whether template buttons use `type="button"` in a `div` or a nested `form` without nested forms — must not break manual form submit.

</decisions>

<canonical_refs>

## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Bob tasks and security
- `docs/api/bob-interaction.md` — POST/GET contract, validation, UI sections
- `docs/security/README.md` — `ALLOW_BOB_TASKS`, allowlisted argv, rejected entry points
- `.planning/phases/05C-bob-task-entry/05C-CONTEXT.md` — original task create decisions
- `.planning/phases/06A-06B-task-followup-inbox/06A-06B-CONTEXT.md` — post-create highlight, inbox, auto-refresh

### Implementation surface
- `backend/dashboard.py` — dashboard HTML, CSS, `submitBobTask`, Bob history/inbox
- `backend/main.py` — `POST /api/bob/tasks` (no change expected)
- `backend/bob_tasks.py` — server-side validation and kanban create (no change expected)
- `tests/test_api.py` — dashboard content assertions

</canonical_refs>

<code_context>

## Existing Code Insights

### Reusable Assets
- `submitBobTask` (lines ~1016–1055): `fetchJson("/api/bob/tasks", { method: "POST", ... })`, result handling, list refresh, detail open.
- `setBobTaskResult` / `clearBobTaskResult`: shared feedback for create actions.
- `loadBobHistory`, `scheduleBobHighlight`, `loadBobTaskDetail`: post-success UX from 6A–6B.
- `updateBobTasksUi`: toggles `#bob-task-form` and related sections from status payload `allow_bob_tasks`.
- `.bob-section`, `.action-row`, `.action-result`, `.bob-inbox-item` card patterns for consistent styling.

### Established Patterns
- Single-file dashboard: all UI in `backend/dashboard.py` (no separate frontend bundle).
- Norwegian labels; feature gated by server flags in `/api/status`.
- Tests assert dashboard HTML strings in `tests/test_api.py`.

### Integration Points
- `#bob-task-section` — add template markup and JS before `#bob-task-form`.
- Status bootstrap — templates respect same `bobTasksEnabled` flag as manual form.

</code_context>

<specifics>

## Specific Ideas

- Section title: **Bob task-maler**; manual section keeps **Send oppgave til Bob**.
- Five predefined templates as listed in D-10 table (user-provided prompts locked).
- Verification: `npm run lint`, `npm run build`, manual template send + list refresh; Bob deploy unchanged except pull/build/kickstart if needed.

</specifics>

<deferred>

## Deferred Ideas

- User-editable or server-stored template library — new capability, own phase.
- Extra modal to collect URL for «Analyser nettside» — URL request stays in task body for Bob agent (per template prompt).
- Template categories, favorites, or scheduling — out of scope.
- Any new write routes, service actions, terminal, chat, or `hermes -z`.

</deferred>

---

*Phase: 6C-Task Templates*
*Context gathered: 2026-06-04*
