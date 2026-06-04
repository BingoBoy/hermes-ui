# Phase 6G: Implementation Log

## 2026-06-04

- Added dashboard helper `taskResultValue(task)`.
- Updated result detection, excerpt, copy text, and detail rendering to use `task.result` first, then `latest_summary`.
- Detail view now passes top-level `payload.latest_summary` into the display task when `task.result` is empty.
- Added a focused dashboard test assertion for `taskResultValue` / `latest_summary`.
