# CLAUDE.md

Instructions for working in this project. Read this before every session.

---

## What This Project Is

A personal stock portfolio monitoring platform. It pulls data from Trading212, processes it through a medallion data pipeline, and surfaces it on a React dashboard. The goal is a single place to understand portfolio performance, risk, and opportunities — metrics Trading212 doesn't provide.

Solo project. One developer wearing all hats.

---

## Repository Layout

```text
portfolio-management-platform/
├── vault/                  ← all runnable code lives here
│   ├── backend/            ← FastAPI + domain services
│   ├── frontend/           ← React (Vite + MUI) — primary UI
│   ├── legacy/             ← Dash dashboard (kept, not active development)
│   ├── pipeline/           ← ETL pipelines + Prefect orchestration
│   ├── shared/             ← DB client, base repos, utilities
│   ├── migrations/         ← Alembic migrations (4 tracks)
│   ├── prefect.yaml        ← Prefect deployment config
│   └── pyproject.toml
├── docs/                   ← documentation
├── tests/                  ← test suite
├── scripts/                ← deploy and git helper scripts
└── sandbox/                ← EDA queries, scratch work
```

**All commands are run from `vault/`.**

---

## Architecture

Four layers. Keep changes within one layer per task.

```text
Frontend        vault/frontend/                React UI — reads from FastAPI
Orchestration   vault/pipeline/orchestration/  Prefect — schedules pipelines
Backend         vault/pipeline/               ETL pipelines (T212, FRED, history)
                vault/backend/                Domain services (portfolio, rebalancing)
Storage         raw → staging → analytics      Postgres, 3 schemas
```

`vault/shared/` is cross-cutting — not a layer.

Full detail: `docs/architecture.md`

---

## Ports

| Service                 | Port  |
|-------------------------|-------|
| React frontend (dev)    | :5173 |
| FastAPI backend         | :8001 |
| Dash dashboard (legacy) | :8050 |
| Prefect UI              | :4200 |

---

## Before Writing Any Code

1. **Read the existing implementation first.** Find a similar pipeline, component, or pattern already in the codebase and understand it before writing anything new.
2. **Check the relevant doc.** `docs/design/` contains accurate reference docs. `docs/archive/` is stale — do not base code on it.
3. **Confirm the layer.** Make sure the change belongs to one layer only.

---

## Pipelines

All pipelines follow the Source → Transformation → Destination pattern. Each component is a separate class implementing a protocol. The `Pipeline` class wires them together in a `run` method.

**Always read `docs/design/doc-pipelines.md` before building a new pipeline.**

Key base classes in `vault/pipeline/etl/policies.py`:

- `FullLoader` — bronze-tier bulk loads with date partitioning
- `BaseSilverPipeline` — standard extract → validate → upsert flow
- `BaseGoldPipeline` — gold fan-out: one source query → multiple fact destinations

---

## Storage — Medallion Architecture

| Schema      | Layer  | What It Holds                                               |
|-------------|--------|-------------------------------------------------------------|
| `raw`       | Bronze | Append-only, partitioned by date, data as received (JSONB)  |
| `staging`   | Silver | Typed, deduplicated, normalised                             |
| `analytics` | Gold   | Kimball star schema — built to answer dashboard questions   |
| `portfolio` | OLTP   | Asset registry, tags, rebalancing config/plan               |

Schema migrations are managed with Alembic. Four independent tracks — one per schema — each with its own ini file in `vault/migrations/postgres/`.

Schema detail:

- `docs/design/schema-analytics.md` — gold layer (authoritative)
- `docs/design/schema-staging.md` — silver layer (authoritative)

---

## Gold Layer

The gold layer is fully implemented. The `analytics` schema has all dimension tables and six fact tables: `fact_price`, `fact_valuation`, `fact_return`, `fact_technical`, `fact_signal`, `fact_portfolio_daily`.

The canonical gold pipeline is `PipelineT212Gold` (`vault/pipeline/etl/runners/pipeline_gold_t212.py`). It is the single pipeline that writes to all six fact tables. It runs hourly via `flow_t212_gold` (registered in `vault/prefect.yaml`).

**Computation is in the gold layer.** All metrics (moving averages, rolling volatility, LAG-based returns, drawdown) are computed via SQL window functions in `PipelineT212Gold`'s source query. The computed silver tables (`staging.asset_computed`, `staging.account_computed`) exist but are no longer part of the active pipeline.

Do not add gold layer tables or columns speculatively. Only build what a dashboard question requires.

---

## Backend — Domain Layer

`vault/backend/` follows a DDD layout: layers at top, domains as subdivisions.

```text
backend/
├── domain/        — entities, value objects, repo interfaces
├── application/   — use cases (PortfolioService, RebalancingService)
└── infrastructure/ — repo implementations (Postgres)
```

Domains: `portfolio`, `rebalancing`, `credentials`, `strategies`.

**Rule:** repo imports (`infrastructure/`) never appear in `application/` or `domain/`. Services depend on interfaces defined in `domain/`. The API layer (`backend/api/`) calls application services only.

---

## Frontend

React + TypeScript + Vite + MUI + Recharts. Runs on **:5173** in development.

```text
frontend/src/
├── api/         — Axios client, one file per resource
├── components/  — atoms → molecules → organisms + charts
├── hooks/       — React Query data hooks
├── layouts/     — page shell and nav
├── pages/       — page-level components
├── presenters/  — view model transforms
├── store/       — Zustand global state
└── theme/       — MUI tokens
```

The frontend proxies `/api` to FastAPI. All data comes from `GET /api/*` endpoints — no direct DB access from the frontend.

---

## Known Gaps — Docs vs. Code

- **Tagging model:** The domain entity uses `tag_type_id`; the DB column is `category_id`. The repository layer maps between them. Both names are correct in their respective contexts.
- `schema-staging.md` is the most accurate staging schema doc.
- `schema-analytics.md` reflects the current implemented schema.

---

## Working Rules

Rules are formalised in `.claude/rules/`. Key rules:

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

---

## Key Docs

| Doc                                | What it covers                                             |
|------------------------------------|------------------------------------------------------------|
| `docs/architecture.md`             | Layer diagram, folder structure, key decisions             |
| `docs/setup.md`                    | Getting the project running                                |
| `docs/commands.md`                 | Every useful command                                       |
| `docs/design/doc-pipelines.md`     | Pipeline creation guide — read before building a pipeline  |
| `docs/design/schema-analytics.md`  | Gold schema reference                                      |
| `docs/design/schema-staging.md`    | Silver schema reference                                    |
| `docs/design/metrics-reference.md` | Dashboard metrics catalogue and formulas                   |
| `docs/design/ui-design.md`         | Dashboard tab layout and table→column mappings             |
| `docs/design/ui-lingo.md`          | Dash component vocabulary (for legacy dashboard work)      |
| `docs/integrations/fred-api.md`    | FRED API reference                                         |

---

## Testing

### Definition of done

No code change is complete without a corresponding test. This is not optional.

Every PR or task must include:

- Unit tests for any new domain logic or presenter function
- Integration tests for any new service method
- Updated tests for any modified behaviour

### What to test where

```text
domain/          → pure unit tests, no mocks needed
application/     → mock ports (inject fakes, not mocks)
api/routers/     → FastAPI TestClient, test HTTP contracts
pipeline/        → test each use case with fake adapters
frontend/        → component tests for presenters, not render details
```

### Before writing any code

1. Read the existing tests for the area you're changing
2. Identify what's missing or outdated
3. Propose a test plan before implementing
4. Wait for confirmation, then implement code + tests together

### Test commands

```bash
pytest backend/tests/ -x -q          # run all, stop on first failure
pytest backend/tests/domain/ -v      # domain only
pytest backend/tests/ --cov=backend  # with coverage
```

---

## Skills Available

- `/database` — schema reference for all three layers, query rules, migration commands
- `/pipeline` — pipeline pattern, failure modes, pipeline inventory, migration safety
- `/ui` — dashboard layout rules, component IDs, callback safety checks, theme wiring
- `/financial-analyst` — metrics catalogue, dashboard KPI suggestions
- `/docs` — doc map, trustworthiness ratings, update checklist by change type
