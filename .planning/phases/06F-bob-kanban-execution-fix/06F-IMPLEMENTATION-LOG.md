# Phase 6F: Implementation Log

## 2026-06-04

- Added `HERMES_BOB_TASK_ASSIGNEE` to backend settings.
- Added strict server-side assignee validation.
- Updated `hermes kanban create` argv builder to append `--assignee <profile>` only when the server env var is set and valid.
- Kept API request contract at `title` + `body`; client-provided `assignee` is ignored.
- Added API error handling for invalid server assignee configuration.
- Added `/api/status` fields for safe assignee visibility:
  - `bob_task_assignee`
  - `bob_task_assignee_configured`
  - `bob_task_assignee_valid`
- Updated tests and Bob task / security / deployment docs.
