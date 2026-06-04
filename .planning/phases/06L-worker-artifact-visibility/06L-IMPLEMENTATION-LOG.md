# Phase 6L: Implementation Log

## 2026-06-04

- Added safe artifact extraction to `backend/bob_tasks.py`.
- Existing `GET /api/bob/tasks/{id}` can now include `artifacts`.
- Artifact reads are bounded to 3 files, 20 KB each, text suffixes only.
- Artifact paths must resolve under the task workspace.
- Added artifact rendering to Bob task detail in `backend/dashboard.py`.
- Added `Kopier artifakt` action for artifact content.
- Added tests for safe artifact inclusion and path escape rejection.
