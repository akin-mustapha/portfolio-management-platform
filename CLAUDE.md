# CLAUDE.md

Instructions for working in this project. Read this before every session.

---

## What This Project Is

A personal stock portfolio monitoring system. It pulls data from Trading212, processes it through a data pipeline, and surfaces it on a Dash dashboard. The goal is a single place to understand portfolio performance, risk, and opportunities — metrics Trading212 doesn't provide.

---

## Architecture

Four layers. Keep changes within one layer per task.

```text
Frontend        src/dashboard/            Dash UI — reads from services
Orchestration   src/orchestration/        Prefect — schedules pipelines
Backend         src/pipelines/            ETL pipelines and Kafka events
                src/backend/services/     Portfolio domain logic
Storage         raw → staging → analytics (Postgres, 3 schemas)
```

`src/shared/` and `src/config/` are cross-cutting — not a layer.

Full detail: `docs/02-architecture/architecture.md`

---

## Before Writing Any Code

1. **Read the existing implementation first.** Find a similar pipeline, component, or pattern already in the codebase and understand it before writing anything new.
2. **Check the relevant doc.** Not all docs are accurate yet — treat them as intent, not ground truth. The code is the authority.
3. **Confirm the layer.** Make sure the change belongs to one layer only.

---

## Pipelines

All pipelines follow the Source / Transformation / Destination pattern. Each component is a separate class implementing a protocol. The `Pipeline` class wires them together in a `run` method.

**Always read `doc-pipelines.md` before building a new pipeline.**
Reference: `docs/02-architecture/design/ingestion/doc-pipelines.md`

---

## Storage — Medallion Architecture

| Schema | Layer | What It Holds |
| --- | --- | --- |
| `raw` | Bronze | Append-only, partitioned by date, data as received |
| `staging` | Silver | Typed, deduplicated, normalised |
| `analytics` | Gold | Kimball star schema — built to answer dashboard questions |

Schema migrations are managed with Alembic.
Schema detail: `docs/02-architecture/design/schema/`

---

## Gold Layer

The gold layer is fully implemented and orchestrated. The `analytics` schema, all dimension tables, and all six fact tables (`fact_price`, `fact_valuation`, `fact_return`, `fact_technical`, `fact_signal`, `fact_portfolio_daily`) exist and are fully migrated.

The canonical gold pipeline is `PipelineT212Gold` (`src/pipelines/application/runners/pipeline_gold_t212.py`). It is the single pipeline that writes to all six fact tables. It runs hourly via `flow_t212_gold` (registered in `prefect.yaml`).

**Computation is in the gold layer.** All metrics (moving averages, rolling volatility, LAG-based returns, drawdown) are computed via SQL window functions in `PipelineT212Gold`'s source query. The computed silver tables (`staging.asset_computed`, `staging.account_computed`) exist but are no longer part of the active pipeline.

Dashboard questions are tracked in: `docs/02-architecture/design/ui-design.md`
Schema reference: `docs/02-architecture/design/schema/schema-analytics.md`

Do not add gold layer tables or columns speculatively. Only build what a dashboard question requires.

---

## Known Gaps — Docs vs. Code

- The docs and code are not fully aligned. Treat docs as design intent.
- **Tagging model:** The domain entity uses `tag_type_id`; the DB column is `category_id`. The repository layer maps between them. Both names are correct in their respective contexts.
- `schema-staging.md` is the most accurate schema doc.
- `schema-analytics.md` reflects the current implemented schema (post-migration-008).

---

## Working Rules

Rules are formalized in `.claude/rules/`. Key rules:

- **Layer segregation** — one task, one layer; no cross-layer changes in a single branch
- **Read before write** — read the file before proposing changes
- **No speculation** — no fields, tables, or features without a specific requirement
- **No over-engineering** — no abstractions or configurability beyond what the task needs
- **Migrations** — every schema change needs an Alembic migration; never reference unapplied columns
- **Dashboard callbacks** — search for duplicate `Output(...)` before adding; confirm layout direction
- **Refactoring** — verify imports resolve in both Prefect and dashboard contexts after multi-file changes

---

## Git & Branching

- Branches are always linked to a GitHub issue
- Branch format: `feature/issue-123-description` or `bug/issue-42-description`
- One layer per branch
- Squash merge to `dev`, rebase-merge `dev` to `main`
- PRs require at least one approval

Full workflow: `docs/03-engineering/doc-project-workflow.md`

---

## Skills Available

- `/database` — schema reference for all three layers, query rules, migration commands
- `/pipeline` — pipeline pattern, failure modes, pipeline inventory, migration safety
- `/dashboard` — layout rules, component IDs, callback safety checks, theme wiring
- `/docs` — doc map, trustworthiness ratings, update checklist by change type
- `/financial-analyst` — metrics catalogue, dashboard KPI suggestions
- `/project-navigation` — navigating the codebase (incomplete)
