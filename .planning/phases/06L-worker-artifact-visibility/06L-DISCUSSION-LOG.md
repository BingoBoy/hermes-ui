# Phase 6L: Discussion Log

## 2026-06-04

Bob completed task `t_7b978d4f` has worker artifact metadata:

- `task.workspace_path`: `/Users/trulsdahl/.hermes/kanban/workspaces/t_7b978d4f`
- `runs[0].metadata.file_path`: `/Users/trulsdahl/.hermes/kanban/workspaces/t_7b978d4f/morgenbrief.md`

Decision:

- Add artifact content only to existing task detail response.
- Do not add a file path endpoint.
- Do not let the browser request arbitrary paths.
- Only expose files that:
  - resolve under the task workspace
  - have allowed text suffix: `.md`, `.txt`, `.json`
  - are at most 20 KB
  - are discovered from kanban show metadata
- Return relative path, size, and text content.
