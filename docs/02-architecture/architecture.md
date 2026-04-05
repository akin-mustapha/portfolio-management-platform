# Architecture

Four layers. Each has a single responsibility.

```
┌─────────────────────────────────┐
│           Frontend              │  Dash UI — portfolio & asset views
├─────────────────────────────────┤
│         Orchestration           │  Prefect — schedules and coordinates pipelines
├─────────────────────────────────┤
│           Backend               │  Pipelines, events, services
├─────────────────────────────────┤
│           Storage               │  raw → staging → analytics
└─────────────────────────────────┘
```

---

## Frontend (`src/dashboard/`)

Dash application. Reads from the analytics (gold) layer via backend services.
Does no data transformation — only displays what services provide.

Internal structure:

```
assets/          — CSS split by concern: theme, base, layout, components, charts, ag-grid
api/             — Flask/Dash server-side API routes
components/      — shared UI primitives (atoms only at this level)
  atoms/         — pure primitives: value formatters, badge elements
layouts/         — top-level shell: navbar, page router, settings modal
pages/portfolio/ — portfolio page: layout, tabs, callbacks, charts
  tabs/          — one file per tab: Valuation, Risk, Opportunities, Asset Profile
  charts/        — chart implementations: portfolio_charts, asset_charts
  callbacks/     — callbacks package split by concern: data, filters, selection, tags, ui, theme, settings
  components/    — atomic design: atoms → molecules → organisms
    atoms/       — pure primitives: value formatters, badge elements
    molecules/   — atoms with a single job: KPI cards
    organisms/   — full sections: KPI row, table, filter bar, tab assembler
controllers/     — orchestrate data fetch and presenter calls
presenters/      — transform DB data into dashboard-ready view models
infrastructure/  — SQL queries against analytics schema
utils/           — dashboard-local utility functions
```

## Orchestration (`src/orchestration/`)

Prefect. Defines when and in what order pipelines run.
Sits above the backend — coordinates it, doesn't contain business logic.

## Backend (`src/backend/` and `src/pipelines/`)

**Pipelines** (`src/pipelines/`) — Pulls data from Trading212. Loads into raw, transforms through staging, computes and writes to analytics (gold).

- `domain/` — core models: Data and Event; Pydantic schemas per layer (bronze/, silver/, gold/)
- `application/` — pipeline logic: protocols, policies, runners (bronze, silver, gold, loaders, events), interfaces, validators
- `infrastructure/` — external integrations: Trading212 API client, Kafka producer/consumer, database repositories, SQL queries (gold/, silver/)
- `factories/` — PipelineFactory and EventProducerFactory registries

**Services** (`src/backend/`) — Business logic layer between storage and frontend.
Current domains: `portfolio/`, `credentials/`, and `rebalancing/`.

- `domain/` — entities per domain: portfolio (Asset, Tag, Category, AssetTag, Industry, Sector), rebalancing
- `application/` — use case interfaces and repository contracts per domain (portfolio/, rebalancing/)
- `infrastructure/` — repository implementations (Postgres and SQLite) per domain (portfolio/, credentials/, rebalancing/)

## Storage (`raw` → `staging` → `analytics`)

Three-schema medallion architecture inside Postgres.

| Schema | Also Called | What It Holds |
|--------|-------------|---------------|
| `raw` | Bronze | Append-only partitioned data, exactly as received |
| `staging` | Silver | Typed, deduplicated, computed metrics |
| `analytics` | Gold | Kimball star schema — built to answer dashboard questions |

Schema detail: `docs/02-architecture/design/schema/`

## Cross-cutting

`src/shared/` — database connections, repositories, utilities used across all layers.
`src/config/` — environment and app configuration.
