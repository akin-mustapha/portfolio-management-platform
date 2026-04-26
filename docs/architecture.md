# Architecture

Four layers. Keep changes within one layer per task.

```
┌─────────────────────────────────┐
│           Frontend              │  React UI (primary) + Dash UI (legacy)
├─────────────────────────────────┤
│         Orchestration           │  Prefect — schedules and coordinates pipelines
├─────────────────────────────────┤
│           Backend               │  Pipelines, events, services, FastAPI
├─────────────────────────────────┤
│           Storage               │  raw → staging → analytics
└─────────────────────────────────┘
```

All code lives under `vault/`. Commands are run from `vault/`.

---

## Frontend

The project has two frontends. React is primary; Dash is legacy.

### React frontend (`vault/frontend/`)

Vite + React + TypeScript + MUI + Recharts. Dev server on **:5173**.
Reads all data from the FastAPI backend at `vault/backend/api/` (**:8001**).

```
frontend/src/
├── api/            — Axios client, one file per resource
├── components/     — atoms → molecules → organisms + charts
├── hooks/          — React Query data hooks
├── layouts/        — page shell and navigation
├── pages/          — page-level components
├── presenters/     — view model transforms
├── store/          — Zustand global state
├── theme/          — MUI theme tokens and config
└── utils/          — chart formatters and helpers
```

### Dash dashboard (`vault/legacy/dashboard/`)

Legacy Dash application. Served on **:8050**. Reads from the analytics (gold) layer via backend services. No data transformation — only displays what services provide.

```
legacy/dashboard/
├── assets/         — CSS: theme, base, layout, components, charts
├── api/            — Flask/Dash server-side API routes
├── layouts/        — navbar, page router, settings modal
├── pages/portfolio/
│   ├── tabs/       — Valuation, Risk, Opportunities, Asset Profile
│   ├── charts/     — portfolio_charts, asset_charts
│   └── callbacks/  — data, filters, selection, tags, ui, theme, settings
├── components/     — atoms → molecules → organisms
├── controllers/    — orchestrate data fetch and presenter calls
├── presenters/     — transform DB rows into dashboard-ready view models
├── infrastructure/ — SQL queries against analytics schema
└── utils/
```

---

## API (`vault/backend/api/`)

FastAPI application served on **:8001**. Exposes REST endpoints consumed by the React frontend.

```
backend/api/
├── main.py             — FastAPI app entry point
├── routers/            — one file per resource: portfolio, assets, tags, rebalance, credentials
├── serialization.py    — shared response models
└── dependencies.py     — DB session, shared deps
```

Routers delegate to application-layer services in `vault/backend/application/`. No business logic in routers.

---

## Orchestration (`vault/pipeline/orchestration/`)

Prefect. Defines when and in what order pipelines run. Sits above the backend — coordinates it, does not contain business logic. Schedules are defined in `vault/prefect.yaml`.

Current flows: `flow_t212_bronze`, `flow_t212_silver`, `flow_t212_gold`, `flow_t212_history_bronze`, `flow_fred`, `flow_rebalance_plan`, `asset_flow_portfolio`, `enrichment_synchronization`.

---

## Backend

### Pipelines (`vault/pipeline/`)

Pulls data from Trading212 and FRED. Loads into raw, transforms through staging, computes and writes to analytics (gold).

```
pipeline/
├── domain/
│   ├── models.py           — Data and Event dataclasses
│   └── schemas/            — Pydantic contracts per layer (bronze/, silver/, gold/)
├── etl/
│   ├── protocols.py        — Source, Transformation, Destination protocols
│   ├── policies.py         — Pipeline, BaseSilverPipeline, FullLoader, BaseGoldPipeline
│   ├── validators/         — SchemaValidator, DeadLetterDestination
│   ├── interfaces/         — API client and database client interfaces
│   ├── runners/            — pipeline implementations (bronze, silver, gold, history, fred)
│   ├── loaders/            — bronze-tier full loaders
│   └── events/             — Trading212 event producer and consumer
├── infrastructure/
│   ├── clients/            — API clients (Trading212, FRED)
│   ├── factories/          — PipelineFactory, EventProducerFactory
│   ├── kafka/              — Kafka producer/consumer adapters
│   ├── queries/            — SQL queries (bronze/, silver/, gold/)
│   └── repositories/       — DB write implementations + dead letter destination
└── orchestration/          — Prefect flow definitions
```

**Pipeline pattern:** every pipeline follows Source → Transformation → Destination, each as a separate class implementing a protocol. The `Pipeline` class (or a base subclass) wires them in `run()`.

**Gold pipeline:** `PipelineT212Gold` (`vault/pipeline/etl/runners/pipeline_gold_t212.py`) is the single pipeline that writes to all six fact tables. All computation (moving averages, rolling volatility, LAG-based returns, drawdown) is done via SQL window functions in the source query — no Python computation.

See `docs/design/doc-pipelines.md` for the full pipeline creation guide.

### Services (`vault/backend/`)

Business logic between storage and the API. Follows a DDD layout: layers at the top, domains as subdivisions.

```
backend/
├── domain/
│   ├── portfolio/       — Asset (aggregate root), Tag, Category, AssetTag, Industry, Sector + repo interfaces
│   ├── rebalancing/     — RebalanceConfig, RebalancePlan + repo interfaces
│   ├── credentials/     — (no domain entity — pure infra)
│   └── strategies/
├── application/
│   ├── portfolio/       — PortfolioService
│   ├── rebalancing/     — RebalancingService, plan_generator
│   ├── credentials/
│   └── strategies/
└── infrastructure/
    ├── portfolio/       — asset, tag, category, sector, industry repos + factory
    ├── rebalancing/     — rebalance_config, rebalance_plan repos + factory
    └── credentials/     — CredentialsRepository
```

---

## Storage (`raw` → `staging` → `analytics`)

Three-schema medallion architecture inside Postgres.

| Schema | Also Called | What It Holds |
|--------|-------------|---------------|
| `raw` | Bronze | Append-only partitioned data, exactly as received (JSONB) |
| `staging` | Silver | Typed, deduplicated, normalised — source of truth for application reads |
| `analytics` | Gold | Kimball star schema — pre-computed, built to answer dashboard questions |

A fourth schema, `portfolio`, holds OLTP tables (asset registry, tags, rebalancing config/plan).

Migrations are managed with Alembic. Four independent tracks — one per schema — each with its own ini file in `vault/migrations/postgres/`.

Schema detail:
- `docs/design/schema-analytics.md` — gold layer (authoritative, post-migration current)
- `docs/design/schema-staging.md` — silver layer (authoritative)

---

## Cross-cutting

`vault/shared/` — database connections, base repository, utilities used across all layers.

---

## Key decisions

- **Port/adapter (DIP):** infrastructure imports never appear outside `infrastructure/` or `factories/`. Services depend on interfaces, not implementations.
- **No computation in application layer:** all metrics (MA, volatility, drawdown, VaR) are SQL window functions in the gold pipeline source query.
- **One layer per branch:** frontend, pipeline, backend, and storage changes never mix in the same PR.
- **Medallion architecture:** raw → staging → analytics; downstream layers never write back upstream.
- **Dead letter queue:** gold pipeline validation failures are written to `monitoring` schema rather than halting the run.
