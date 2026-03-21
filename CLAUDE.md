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
Backend         src/backend/ingestion/    ETL pipelines and Kafka events
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
| `staging` | Silver | Typed, deduplicated, computed metrics |
| `analytics` | Gold | Built to answer dashboard questions (not yet built) |

Schema migrations are managed with Alembic.
Schema detail: `docs/02-architecture/design/schema/`

---

## Gold Layer — Not Yet Built

`pipeline_asset_gold.py` exists but is a copy of the silver pipeline — it does not write to `analytics`. The gold layer is being designed **dashboard-question-first**: define what the dashboard needs to show, then build the tables to answer those questions.

Dashboard questions are tracked in: `docs/02-architecture/design/ui-design.md`
Planned schema (draft only, not final): `docs/02-architecture/design/schema/schema-analytics.md`

Do not implement gold layer tables speculatively. Only build what a dashboard question requires.

---

## Known Gaps — Docs vs. Code

- The docs and code are not fully aligned. Treat docs as design intent.
- `doc-data-model.md` describes the tagging model but some field names have drifted (e.g. `tag_type` in docs is `Category` in code).
- `schema-staging.md` is the most accurate schema doc.
- Gold layer docs describe a planned design, not current state.

---

## Working Rules

**Layer segregation** — One task, one layer. Do not mix ingestion changes with dashboard changes in the same branch.

**Read before write** — Never suggest changes to code you haven't read.

**No speculation** — Don't add fields, tables, or features not tied to a specific requirement or dashboard question.

**No over-engineering** — Don't add abstractions, error handling, or configurability beyond what the task needs.

**Migrations** — Any new or changed table requires an Alembic migration. See `docs/03-engineering/doc-commands.md`.

**Dashboard callbacks** — Before adding any callback output, search for existing `Output('component-id', 'property')` patterns to avoid duplicates. For layout direction (horizontal vs vertical), confirm with the user before implementing — default to side-by-side for chart pairs.

**Schema changes** — Never reference columns from unapplied migrations in application code. Confirm migrations are applied before writing code that reads those columns.

**Refactoring** — Do not remove variables that appear unused without first searching templates, callbacks, and conditional logic (especially theme variables like `ct`). After any multi-file refactor, run the test suite and verify all imports resolve — Prefect workers and the dashboard app may resolve imports differently.

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
