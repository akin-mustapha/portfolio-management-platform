---
name: layer-segregation
description: One task, one layer — do not mix pipeline and dashboard changes in a single branch
---

One task, one layer. Do not mix ingestion/pipeline changes with dashboard changes in the same branch or PR.

The four layers are:
- `src/dashboard/` — Frontend
- `src/orchestration/` — Orchestration
- `src/pipelines/` + `src/backend/services/` — Backend
- Postgres schemas (`raw`, `staging`, `analytics`) — Storage
